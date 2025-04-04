/* (c) 2014 - 2016 Open Source Geospatial Foundation - all rights reserved
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.wcs2_0;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import javax.xml.namespace.QName;
import org.geoserver.catalog.CoverageInfo;
import org.geoserver.catalog.DimensionPresentation;
import org.geoserver.catalog.ResourceInfo;
import org.geoserver.data.test.CiteTestData;
import org.geoserver.data.test.SystemTestData;
import org.geoserver.wcs.CoverageCleanerCallback;
import org.geoserver.wcs2_0.response.GranuleStack;
import org.geotools.api.coverage.grid.GridCoverageReader;
import org.geotools.api.parameter.ParameterValue;
import org.geotools.coverage.grid.GridCoverage2D;
import org.geotools.gce.imagemosaic.ImageMosaicFormat;
import org.geotools.geometry.jts.ReferencedEnvelope;
import org.geotools.referencing.CRS;
import org.junit.BeforeClass;
import org.junit.Test;
import org.springframework.mock.web.MockHttpServletResponse;

public class WCSMultiDimSubsetTest extends WCSNetCDFBaseTest {
    private static final QName LAMBERTMOSAIC = new QName(CiteTestData.WCS_URI, "lambert", CiteTestData.WCS_PREFIX);

    @BeforeClass
    public static void init() {
        WCSNetCDFBaseTest.init();
        System.setProperty("testdata.force.delete", "true");
    }

    @Override
    protected void setUpTestData(SystemTestData testData) throws Exception {
        super.setUpTestData(testData);
        testData.setUpDefaultRasterLayers();
    }

    @Override
    protected void onSetUp(SystemTestData testData) throws Exception {
        // workaround to add our custom multi dimensional format

        super.onSetUp(testData);
        testData.addRasterLayer(LAMBERTMOSAIC, "lambertmosaic.zip", null, null, this.getClass(), getCatalog());
        String coverageName = getLayerId(LAMBERTMOSAIC);
        setupRasterDimension(coverageName, ResourceInfo.TIME, DimensionPresentation.LIST, null);
        CoverageInfo info = getCatalog().getCoverageByName(coverageName);
        // Add this to prevent resource locking due to deferred disposal
        info.getParameters().put("USE_JAI_IMAGEREAD", "false");
        getCatalog().save(info);
    }

    /** Tests if we can select a single pixel value using a WCS request */
    @Test
    public void sliceLambert() throws Exception {

        // check we can read it as a TIFF and it is similare to the original one
        GridCoverage2D targetCoverage = null, sourceCoverage = null;
        GridCoverageReader coverageReader = null;
        try {

            // === slicing on Y axis
            // source
            CoverageInfo coverageInfo = this.getCatalog().getCoverageByName(LAMBERTMOSAIC.getLocalPart());
            coverageReader = coverageInfo.getGridCoverageReader(null, null);
            final ParameterValue<Boolean> useJAI = ImageMosaicFormat.USE_JAI_IMAGEREAD.createValue();
            useJAI.setValue(false);
            sourceCoverage = (GridCoverage2D) coverageReader.read(useJAI);
            final ReferencedEnvelope sourceEnvelope = sourceCoverage.getEnvelope2D();

            // subsample using the original extension
            MockHttpServletResponse response = getAsServletResponse("wcs?request=GetCoverage&service=WCS&version=2.0.1"
                    + "&coverageId=wcs__lambert&&Format=application/custom"
                    + "&subset=E,http://www.opengis.net/def/crs/EPSG/0/31300("
                    + sourceEnvelope.getMinX()
                    + ","
                    + (sourceEnvelope.getMinX() + 25)
                    + ")"
                    + "&subset=N,http://www.opengis.net/def/crs/EPSG/0/31300("
                    + sourceEnvelope.getMinY()
                    + ","
                    + (sourceEnvelope.getMinY() + 25)
                    + ")");

            assertNotNull(response);
            targetCoverage =
                    applicationContext.getBean(WCSResponseInterceptor.class).getLastResult();

            assertTrue(CRS.equalsIgnoreMetadata(
                    sourceCoverage.getCoordinateReferenceSystem(), targetCoverage.getCoordinateReferenceSystem()));

            assertTrue(targetCoverage instanceof GranuleStack);
            GridCoverage2D firstResult =
                    ((GranuleStack) targetCoverage).getGranules().get(0);

            // checks
            assertEquals(1, firstResult.getGridGeometry().getGridRange().getSpan(0));
            assertEquals(1, firstResult.getGridGeometry().getGridRange().getSpan(1));
            assertEquals(0, firstResult.getGridGeometry().getGridRange().getLow(0));
            assertEquals(1, firstResult.getGridGeometry().getGridRange().getLow(1));

        } finally {
            if (coverageReader != null) {
                try {
                    coverageReader.dispose();
                } catch (Exception e) {
                    // Ignore it
                }
            }
            if (targetCoverage != null) {
                try {
                    CoverageCleanerCallback.disposeCoverage(targetCoverage);
                } catch (Exception e) {
                    // Ignore it
                }
            }
            if (sourceCoverage != null) {
                try {
                    CoverageCleanerCallback.disposeCoverage(sourceCoverage);
                } catch (Exception e) {
                    // Ignore it
                }
            }
        }
    }
}
