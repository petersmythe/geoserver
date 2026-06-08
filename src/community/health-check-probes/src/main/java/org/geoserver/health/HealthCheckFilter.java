/* (c) 2026 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.health;

import jakarta.servlet.FilterChain;
import jakarta.servlet.FilterConfig;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.logging.Logger;
import org.geoserver.filters.GeoServerFilter;
import org.geotools.util.logging.Logging;

/**
 * A servlet filter that intercepts health check requests at {@code /management/health/**} and handles them directly.
 * Implements {@link GeoServerFilter} so it is automatically picked up by GeoServer's {@code SpringDelegatingFilter}.
 *
 * <p>Supported endpoints:
 *
 * <ul>
 *   <li>{@code /management/health/liveness} - Always returns 200 with {@code {"status":"UP"}}
 *   <li>{@code /management/health/readiness} - Returns 200/UP when ready, 503/DOWN when not ready
 * </ul>
 *
 * <p>Non-GET methods receive HTTP 405 Method Not Allowed. Unknown paths under {@code /management/health/} receive HTTP
 * 404 Not Found.
 */
public class HealthCheckFilter implements GeoServerFilter {

    private static final Logger LOGGER = Logging.getLogger(HealthCheckFilter.class);

    private final ReadinessStateBean readinessState;

    public HealthCheckFilter(ReadinessStateBean readinessState) {
        this.readinessState = readinessState;
        LOGGER.info("HealthCheckFilter initialized with ReadinessStateBean");
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpReq = (HttpServletRequest) request;
        String path = httpReq.getServletPath() + (httpReq.getPathInfo() != null ? httpReq.getPathInfo() : "");

        if (path.startsWith("/management/health/")) {
            handleHealthRequest(httpReq, (HttpServletResponse) response, path);
        } else {
            chain.doFilter(request, response);
        }
    }

    private void handleHealthRequest(HttpServletRequest req, HttpServletResponse resp, String path) throws IOException {
        if (!"GET".equalsIgnoreCase(req.getMethod())) {
            resp.setStatus(HttpServletResponse.SC_METHOD_NOT_ALLOWED);
            return;
        }

        resp.setContentType("application/json;charset=UTF-8");

        if (path.equals("/management/health/liveness")) {
            resp.setStatus(HttpServletResponse.SC_OK);
            resp.getWriter().write("{\"status\":\"UP\"}");
        } else if (path.equals("/management/health/readiness")) {
            try {
                boolean ready = readinessState.isReady();
                if (ready) {
                    resp.setStatus(HttpServletResponse.SC_OK);
                    resp.getWriter().write("{\"status\":\"UP\"}");
                } else {
                    LOGGER.fine("Readiness check: returning DOWN");
                    resp.setStatus(HttpServletResponse.SC_SERVICE_UNAVAILABLE);
                    resp.getWriter().write("{\"status\":\"DOWN\"}");
                }
            } catch (Exception e) {
                LOGGER.warning("Readiness check failed with exception: " + e.getMessage());
                resp.setStatus(HttpServletResponse.SC_SERVICE_UNAVAILABLE);
                resp.getWriter().write("{\"status\":\"DOWN\"}");
            }
        } else {
            resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
        }
    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {}

    @Override
    public void destroy() {}
}
