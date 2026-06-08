/* (c) 2026 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.health;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Before;
import org.junit.Test;

/** Unit tests for {@link ReadinessStateBean} verifying state transitions through the GeoServer lifecycle. */
public class ReadinessStateBeanTest {

    private ReadinessStateBean bean;

    @Before
    public void setUp() {
        bean = new ReadinessStateBean();
    }

    @Test
    public void testInitialStateIsFalse() {
        assertFalse("ReadinessStateBean should start in not-ready state", bean.isReady());
    }

    @Test
    public void testOnApplicationEventSetsReadyToTrue() {
        bean.onApplicationEvent(null);
        assertTrue("Should be ready after ContextRefreshedEvent", bean.isReady());
    }

    @Test
    public void testBeforeReinitializeSetsReadyToFalse() throws Exception {
        bean.onApplicationEvent(null);
        assertTrue(bean.isReady());

        bean.beforeReinitialize(null);
        assertFalse("Should be not-ready after beforeReinitialize", bean.isReady());
    }

    @Test
    public void testReinitializeSetsReadyToTrue() throws Exception {
        assertFalse(bean.isReady());

        bean.reinitialize(null);
        assertTrue("Should be ready after reinitialize", bean.isReady());
    }

    @Test
    public void testFullLifecycleSequence() throws Exception {
        // Initial state: not ready
        assertFalse(bean.isReady());

        // ContextRefreshedEvent fires -> ready
        bean.onApplicationEvent(null);
        assertTrue(bean.isReady());

        // beforeReinitialize -> not ready
        bean.beforeReinitialize(null);
        assertFalse(bean.isReady());

        // reinitialize -> ready again
        bean.reinitialize(null);
        assertTrue(bean.isReady());
    }
}
