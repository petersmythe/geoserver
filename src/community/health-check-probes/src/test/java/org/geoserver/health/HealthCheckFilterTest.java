/* (c) 2026 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.health;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import org.junit.Before;
import org.junit.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/** Unit tests for {@link HealthCheckFilter}. */
public class HealthCheckFilterTest {

    private ReadinessStateBean readinessState;
    private HealthCheckFilter filter;

    @Before
    public void setUp() {
        readinessState = new ReadinessStateBean();
        filter = new HealthCheckFilter(readinessState);
    }

    @Test
    public void testLivenessGetReturns200WithStatusUp() throws Exception {
        MockHttpServletRequest request = createRequest("GET", "/management/health/liveness");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, new MockFilterChain());

        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
    }

    @Test
    public void testReadinessGetReturns200WhenReady() throws Exception {
        readinessState.onApplicationEvent(null);

        MockHttpServletRequest request = createRequest("GET", "/management/health/readiness");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, new MockFilterChain());

        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
    }

    @Test
    public void testReadinessGetReturns503WhenNotReady() throws Exception {
        MockHttpServletRequest request = createRequest("GET", "/management/health/readiness");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, new MockFilterChain());

        assertEquals(503, response.getStatus());
        assertEquals("{\"status\":\"DOWN\"}", response.getContentAsString());
    }

    @Test
    public void testNonGetMethodReturns405ForLiveness() throws Exception {
        for (String method : new String[] {"POST", "PUT", "DELETE", "PATCH"}) {
            MockHttpServletRequest request = createRequest(method, "/management/health/liveness");
            MockHttpServletResponse response = new MockHttpServletResponse();

            filter.doFilter(request, response, new MockFilterChain());

            assertEquals("Expected 405 for " + method, 405, response.getStatus());
        }
    }

    @Test
    public void testNonGetMethodReturns405ForReadiness() throws Exception {
        for (String method : new String[] {"POST", "PUT", "DELETE", "PATCH"}) {
            MockHttpServletRequest request = createRequest(method, "/management/health/readiness");
            MockHttpServletResponse response = new MockHttpServletResponse();

            filter.doFilter(request, response, new MockFilterChain());

            assertEquals("Expected 405 for " + method, 405, response.getStatus());
        }
    }

    @Test
    public void testUnknownHealthPathReturns404() throws Exception {
        MockHttpServletRequest request = createRequest("GET", "/management/health/unknown");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, new MockFilterChain());

        assertEquals(404, response.getStatus());
    }

    @Test
    public void testExceptionInIsReadyReturns503() throws Exception {
        ReadinessStateBean mockBean = mock(ReadinessStateBean.class);
        when(mockBean.isReady()).thenThrow(new RuntimeException("Simulated failure"));
        HealthCheckFilter filterWithMock = new HealthCheckFilter(mockBean);

        MockHttpServletRequest request = createRequest("GET", "/management/health/readiness");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filterWithMock.doFilter(request, response, new MockFilterChain());

        assertEquals(503, response.getStatus());
        assertEquals("{\"status\":\"DOWN\"}", response.getContentAsString());
    }

    @Test
    public void testContentTypeIsApplicationJsonUtf8() throws Exception {
        MockHttpServletRequest request = createRequest("GET", "/management/health/liveness");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, new MockFilterChain());

        assertEquals("application/json;charset=UTF-8", response.getContentType());
    }

    @Test
    public void testNonHealthPathPassesThroughToFilterChain() throws Exception {
        MockHttpServletRequest request = createRequest("GET", "/geoserver/wms");
        MockHttpServletResponse response = new MockHttpServletResponse();
        MockFilterChain chain = new MockFilterChain();

        filter.doFilter(request, response, chain);

        assertNotNull("Filter chain should have been invoked", chain.getRequest());
        assertEquals(request, chain.getRequest());
    }

    private MockHttpServletRequest createRequest(String method, String path) {
        MockHttpServletRequest request = new MockHttpServletRequest(method, path);
        request.setServletPath(path);
        return request;
    }
}
