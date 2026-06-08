/* (c) 2026 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.health;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Logger;
import org.geoserver.config.GeoServer;
import org.geoserver.config.GeoServerReinitializer;
import org.geotools.util.logging.Logging;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;

/**
 * Tracks GeoServer's readiness state using lifecycle callbacks. Uses an {@link AtomicBoolean} for thread-safe state
 * tracking between HTTP request threads and GeoServer lifecycle callback threads.
 *
 * <p>The bean starts in a not-ready state. It transitions to ready when the Spring ApplicationContext publishes a
 * {@link ContextRefreshedEvent} (indicating initial startup completion) or when {@link #reinitialize(GeoServer)} is
 * called after a catalog reload. It transitions back to not-ready when {@link #beforeReinitialize(GeoServer)} is called
 * at the start of a reload cycle.
 */
public class ReadinessStateBean implements GeoServerReinitializer, ApplicationListener<ContextRefreshedEvent> {

    private static final Logger LOGGER = Logging.getLogger(ReadinessStateBean.class);

    private final AtomicBoolean ready = new AtomicBoolean(false);

    /**
     * Returns the current readiness state.
     *
     * @return {@code true} if GeoServer is fully initialized and ready to serve requests
     */
    public boolean isReady() {
        return ready.get();
    }

    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        LOGGER.info("ContextRefreshedEvent received — setting readiness to UP");
        ready.set(true);
    }

    @Override
    public void initialize(GeoServer geoServer) throws Exception {
        LOGGER.info("initialize() called — no-op (readiness set via ContextRefreshedEvent)");
    }

    @Override
    public void beforeReinitialize(GeoServer geoServer) throws Exception {
        LOGGER.info("beforeReinitialize() called — setting readiness to DOWN");
        ready.set(false);
    }

    @Override
    public void reinitialize(GeoServer geoServer) throws Exception {
        LOGGER.info("reinitialize() called — setting readiness to UP");
        ready.set(true);
    }
}
