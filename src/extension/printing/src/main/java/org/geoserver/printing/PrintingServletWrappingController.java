/* (c) 2014 - 2016 Open Source Geospatial Foundation - all rights reserved
 * (c) 2001 - 2013 OpenPlans
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.printing;

import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Logger;
import org.geoserver.platform.GeoServerExtensions;
import org.geoserver.platform.GeoServerResourceLoader;
import org.geoserver.platform.resource.Paths;
import org.geoserver.platform.resource.Resource;
import org.geoserver.platform.resource.Resource.Type;
import org.geoserver.platform.resource.Resources;
import org.geoserver.util.IOUtils;
import org.springframework.web.servlet.mvc.ServletWrappingController;

/**
 * Wrapper for Spring's ServletWrappingController to allow use of GeoServer's config dir.
 *
 * @author Alan Gerber, The Open Planning Project
 */
public class PrintingServletWrappingController extends ServletWrappingController {

    private final Logger LOG = org.geotools.util.logging.Logging.getLogger("org.geoserver.printing");

    @Override
    public void setInitParameters(Properties initParameters) {
        // find the config parameter and update it so it points to
        // $GEOSERVER_DATA_DIR/printing/$CONFIG
        String configProp = initParameters.getProperty("config");

        try {
            GeoServerResourceLoader loader = GeoServerExtensions.bean(GeoServerResourceLoader.class);
            String configPath = findPrintConfigDirectory(configProp);
            Resource config = loader.get(configPath);

            if (config.getType() == Type.UNDEFINED) {
                try (InputStream conf = getClass().getResourceAsStream("default-config.yaml")) {
                    IOUtils.copy(conf, config.out());
                }
            }
            if (!Resources.canRead(config)) {
                LOG.warning("Printing module missing its configuration.  Any actions it takes will fail.");
                return;
            }
            initParameters.setProperty("config", config.file().getAbsolutePath());
        } catch (java.io.IOException e) {
            LOG.warning("Unable to calculate canonical path for MapFish printing servlet. "
                    + "Module will fail when run.  IO Exception is: "
                    + e);
        } catch (Exception e) {
            LOG.warning("Unable to access/create config directory for MapFish printing module."
                    + "Module will fail when run. Config exception is: "
                    + e);
        }
        super.setInitParameters(initParameters);
    }

    private String findPrintConfigDirectory(String configProp) {
        // 1. look for environment variable
        String dd = lookupEnvironmentVariable();

        // 2. look up java property
        if (dd == null) {
            dd = lookupSystemProperty();
        }

        // 3. fall back to the default one
        if (dd == null) {
            dd = "printing";
        } else {
            dd = Paths.convert(dd);
        }

        return Paths.path(dd, Paths.convert(configProp));
    }

    String lookupSystemProperty() {
        return System.getProperty("GEOSERVER_PRINT_CONFIG_DIR");
    }

    String lookupEnvironmentVariable() {
        return System.getenv("GEOSERVER_PRINT_CONFIG_DIR");
    }
}
