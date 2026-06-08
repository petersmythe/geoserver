/* (c) 2026 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.health;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import jakarta.servlet.Filter;
import java.util.Base64;
import java.util.Collections;
import java.util.List;
import org.geoserver.test.GeoServerSystemTestSupport;
import org.junit.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/**
 * Integration tests for health check probe endpoints using GeoServerSystemTestSupport. Verifies that the
 * HealthCheckFilter works correctly within the full GeoServer application context.
 */
public class HealthCheckIntegrationTest extends GeoServerSystemTestSupport {

    @Override
    protected List<Filter> getFilters() {
        ReadinessStateBean bean = applicationContext.getBean(ReadinessStateBean.class);
        HealthCheckFilter filter = new HealthCheckFilter(bean);
        return Collections.singletonList(filter);
    }

    @Test
    public void testLivenessReturns200UP() throws Exception {
        MockHttpServletResponse response = getAsServletResponse("management/health/liveness");
        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
        assertTrue(response.getContentType().contains("application/json"));
    }

    @Test
    public void testReadinessReturns200UPAfterContextStarted() throws Exception {
        MockHttpServletResponse response = getAsServletResponse("management/health/readiness");
        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
        assertTrue(response.getContentType().contains("application/json"));
    }

    @Test
    public void testLivenessAccessibleWithoutAuthentication() throws Exception {
        setRequestAuth(null, null);
        MockHttpServletResponse response = getAsServletResponse("management/health/liveness");
        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
    }

    @Test
    public void testReadinessAccessibleWithoutAuthentication() throws Exception {
        setRequestAuth(null, null);
        MockHttpServletResponse response = getAsServletResponse("management/health/readiness");
        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
    }

    @Test
    public void testInvalidCredentialsDoNotTriggerAuthChallenge() throws Exception {
        MockHttpServletRequest request = createRequest("management/health/liveness");
        request.setMethod("GET");
        request.setContent(new byte[] {});
        String invalidCreds = Base64.getEncoder().encodeToString("invaliduser:wrongpassword".getBytes());
        request.addHeader("Authorization", "Basic " + invalidCreds);

        MockHttpServletResponse response = dispatch(request);

        assertEquals(200, response.getStatus());
        assertEquals("{\"status\":\"UP\"}", response.getContentAsString());
        assertNull("No authentication challenge should be issued", response.getHeader("WWW-Authenticate"));
    }

    @Test
    public void testPostMethodReturns405() throws Exception {
        MockHttpServletRequest request = createRequest("management/health/liveness");
        request.setMethod("POST");
        request.setContent(new byte[] {});

        MockHttpServletResponse response = dispatch(request);
        assertEquals(405, response.getStatus());
    }

    @Test
    public void testDeleteMethodReturns405() throws Exception {
        MockHttpServletRequest request = createRequest("management/health/readiness");
        request.setMethod("DELETE");
        request.setContent(new byte[] {});

        MockHttpServletResponse response = dispatch(request);
        assertEquals(405, response.getStatus());
    }

    @Test
    public void testReadinessStateBeanRegistered() {
        ReadinessStateBean bean = applicationContext.getBean("healthCheckReadinessState", ReadinessStateBean.class);
        assertNotNull("ReadinessStateBean should be in application context", bean);
        assertTrue("Should be ready after context startup", bean.isReady());
    }
}
