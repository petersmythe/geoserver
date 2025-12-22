/* (c) 2014 - 2015 Open Source Geospatial Foundation - all rights reserved
 * (c) 2001 - 2013 OpenPlans
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.gwc.layer;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.concurrent.TimeUnit.SECONDS;
import static org.awaitility.Awaitility.await;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.mockito.Mockito.*;

import com.google.common.collect.ImmutableSet;
import com.thoughtworks.xstream.XStream;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;
import org.apache.commons.io.FileUtils;
import org.custommonkey.xmlunit.XMLUnit;
import org.custommonkey.xmlunit.XpathEngine;
import org.custommonkey.xmlunit.exceptions.XpathException;
import org.geoserver.catalog.Catalog;
import org.geoserver.catalog.impl.ModificationProxy;
import org.geoserver.config.util.SecureXStream;
import org.geoserver.platform.GeoServerResourceLoader;
import org.geoserver.platform.resource.FileSystemWatcher;
import org.geoserver.util.DimensionWarning.WarningType;
import org.geowebcache.config.ContextualConfigurationProvider.Context;
import org.geowebcache.config.XMLConfiguration;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;

public class DefaultTileLayerCatalogTest {

    public @Rule TemporaryFolder tmpFolder = new TemporaryFolder();

    private File baseDirectory;

    private GeoServerResourceLoader resourceLoader;

    private DefaultTileLayerCatalog catalog;

    @Before
    public void setUp() throws Exception {
        baseDirectory = tmpFolder.getRoot();
        resourceLoader = new GeoServerResourceLoader(baseDirectory);

        new File(baseDirectory, "gwc-layers").mkdir();

        Supplier<XStream> xStream =
                () -> XMLConfiguration.getConfiguredXStreamWithContext(new SecureXStream(), null, Context.PERSIST);

        catalog = new DefaultTileLayerCatalog(resourceLoader, xStream);
        catalog.initialize();
    }

    @Test
    public void testInitializationSkipsMissingPublishedInfoWhenCatalogProvided() throws Exception {
        Supplier<XStream> xStream =
                () -> XMLConfiguration.getConfiguredXStreamWithContext(new SecureXStream(), null, Context.PERSIST);
        // Create a mock Catalog that reports no published info for id1
        Catalog mockCatalog = mock(Catalog.class);
        when(mockCatalog.getLayer("id1")).thenReturn(null);
        when(mockCatalog.getLayerGroup("id1")).thenReturn(null);

        DefaultTileLayerCatalog catalogWithMock = new DefaultTileLayerCatalog(mockCatalog, resourceLoader, xStream);

        // write a tile layer file referencing id1
        File file = new File(baseDirectory, "gwc-layers/id1.xml");
        writeFileLayerInfoImpl(file, "name1");

        // initialize with the mock catalog; this should skip the file
        catalogWithMock.initialize();

        assertNull(catalogWithMock.getLayerById("id1"));
    }

    @Test
    public void testInitializationLoadsWhenPublishedInfoExists() throws Exception {
        Supplier<XStream> xStream =
                () -> XMLConfiguration.getConfiguredXStreamWithContext(new SecureXStream(), null, Context.PERSIST);
        // Create a mock Catalog that reports a Layer for id1
        Catalog mockCatalog = mock(Catalog.class);
        org.geoserver.catalog.LayerInfo layerInfo = mock(org.geoserver.catalog.LayerInfo.class);
        when(mockCatalog.getLayer("id1")).thenReturn(layerInfo);

        DefaultTileLayerCatalog catalogWithMock = new DefaultTileLayerCatalog(mockCatalog, resourceLoader, xStream);

        // write a tile layer file referencing id1
        File file = new File(baseDirectory, "gwc-layers/id1.xml");
        writeFileLayerInfoImpl(file, "name1");

        // initialize with the mock catalog; this should load the file
        catalogWithMock.initialize();

        assertNotNull(catalogWithMock.getLayerById("id1"));
    }

    @Test
    public void testGetLayerById() {
        GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
        info.setId("id1");
        info.setName("name1");
        catalog.save(info);
        GeoServerTileLayerInfo actual = catalog.getLayerById("id1");
        actual = ModificationProxy.unwrap(actual);
        assertEquals(info, actual);
    }

    @Test
    public void testGetLayerByName() {
        GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
        info.setId("id1");
        info.setName("name1");
        catalog.save(info);
        GeoServerTileLayerInfo actual = catalog.getLayerByName("name1");
        actual = ModificationProxy.unwrap(actual);
        assertEquals(info, actual);
    }

    @Test
    public void testDelete() {
        GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
        info.setId("id1");
        info.setName("name1");
        catalog.save(info);

        GeoServerTileLayerInfo actual = catalog.getLayerByName("name1");
        actual = ModificationProxy.unwrap(actual);
        assertEquals(info, actual);

        GeoServerTileLayerInfo deleted = catalog.delete("id1");
        assertEquals(info, ModificationProxy.unwrap(deleted));

        assertNull(catalog.getLayerById("id1"));
    }

    @Test
    public void testSave() {
        final GeoServerTileLayerInfo original;
        {
            final GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
            info.setId("id1");
            info.setName("name1");
            info.getMimeFormats().add("image/png");
            info.getMimeFormats().add("image/jpeg");

            assertNull(catalog.save(info));

            original = catalog.getLayerById("id1");
            assertEquals(info.getMimeFormats(), original.getMimeFormats());
        }

        original.getMimeFormats().clear();
        original.getMimeFormats().add("image/gif");
        original.setName("name2");

        final GeoServerTileLayerInfo oldValue = catalog.save(original);

        assertNotNull(oldValue);
        assertEquals(ImmutableSet.of("image/png", "image/jpeg"), oldValue.getMimeFormats());
        assertEquals("name1", oldValue.getName());

        assertNull(catalog.getLayerByName("name1"));
        assertNotNull(catalog.getLayerByName("name2"));

        GeoServerTileLayerInfo modified = catalog.getLayerById("id1");
        assertEquals(ImmutableSet.of("image/gif"), modified.getMimeFormats());
    }

    @Test
    public void testSaveWithEmptyStyleParamFilter() {
        final GeoServerTileLayerInfo original;
        {
            final GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
            info.setId("id1");
            info.setName("name1");
            info.getMimeFormats().add("image/png");
            info.getMimeFormats().add("image/jpeg");

            StyleParameterFilter parameterFilter = new StyleParameterFilter();
            parameterFilter.setStyles(Collections.emptySet());
            info.addParameterFilter(parameterFilter);

            assertNull(catalog.save(info));

            original = catalog.getLayerById("id1");
            assertEquals(info.getMimeFormats(), original.getMimeFormats());
        }

        original.getMimeFormats().clear();
        original.getMimeFormats().add("image/gif");
        original.setName("name2");

        final GeoServerTileLayerInfo oldValue = catalog.save(original);

        assertNotNull(oldValue);
        assertEquals(ImmutableSet.of("image/png", "image/jpeg"), oldValue.getMimeFormats());
        assertEquals("name1", oldValue.getName());

        assertNull(catalog.getLayerByName("name1"));
        assertNotNull(catalog.getLayerByName("name2"));

        GeoServerTileLayerInfo modified = catalog.getLayerById("id1");
        assertEquals(ImmutableSet.of("image/gif"), modified.getMimeFormats());
    }

    @Test
    public void testEvents() throws IOException, InterruptedException {

        ((FileSystemWatcher) resourceLoader.getResourceNotificationDispatcher()).schedule(50, MILLISECONDS);

        AtomicBoolean hasBeenCreated = new AtomicBoolean(false);

        AtomicBoolean hasBeenModified = new AtomicBoolean(false);

        AtomicBoolean hasBeenDeleted = new AtomicBoolean(false);

        catalog.addListener((layerId, type) -> {
            switch (type) {
                case CREATE:
                    hasBeenCreated.set(true);
                    break;
                case DELETE:
                    hasBeenDeleted.set(true);
                    break;
                case MODIFY:
                    hasBeenModified.set(true);
                    break;
                default:
                    break;
            }
        });

        File file = new File(baseDirectory, "gwc-layers/id1.xml");

        writeFileLayerInfoImpl(file, "originalname");

        await().atMost(60, TimeUnit.SECONDS).until(hasBeenCreated::get);
        GeoServerTileLayerInfo info = catalog.getLayerById("id1");
        assertEquals("originalname", info.getName());
        assertNotNull(catalog.getLayerByName("originalname"));

        // on linux and older versions of Java the minimim
        long lastModified = file.lastModified();
        await().atMost(1100, MILLISECONDS).until(() -> {
            writeFileLayerInfoImpl(file, "newname");
            return file.lastModified() > lastModified;
        });

        await().atMost(60, SECONDS).until(hasBeenModified::get);

        info = catalog.getLayerById("id1");
        assertEquals("newname", info.getName());
        assertNull(catalog.getLayerByName("originalname"));
        assertNotNull(catalog.getLayerByName("newname"));

        file.delete();

        await().atMost(60, SECONDS).until(hasBeenDeleted::get);

        assertNull(catalog.getLayerById("id1"));
        assertNull(catalog.getLayerByName("newname"));
    }

    @Test
    public void testCreateEventSkippedOnMissingPublishedInfo() throws IOException, InterruptedException {
        ((FileSystemWatcher) resourceLoader.getResourceNotificationDispatcher()).schedule(50, MILLISECONDS);

        AtomicBoolean hasBeenCreated = new AtomicBoolean(false);

        DefaultTileLayerCatalog catalogWithMock = new DefaultTileLayerCatalog(
                mock(Catalog.class),
                resourceLoader,
                () -> XMLConfiguration.getConfiguredXStreamWithContext(new SecureXStream(), null, Context.PERSIST));
        catalogWithMock.addListener((layerId, type) -> {
            if (type == TileLayerCatalogListener.Type.CREATE) {
                hasBeenCreated.set(true);
            }
        });

        File file = new File(baseDirectory, "gwc-layers/id1.xml");
        writeFileLayerInfoImpl(file, "originalname");

        // let the file watcher run for a while
        Thread.sleep(200);

        // since the catalog doesn't provide the referenced published info, the config loader should skip it
        assertFalse(hasBeenCreated.get());
    }

    @Test
    public void testWmtsGetCapabilitiesSkipsStaleGwCLayerFileUnit() throws Exception {
        // Narrow unit-level test that duplicates the original integration intent without booting GeoServer
        final String missingId = "stale-missing-id";

        Supplier<XStream> xStream =
                () -> XMLConfiguration.getConfiguredXStreamWithContext(new SecureXStream(), null, Context.PERSIST);

        // Create a mock Catalog that reports no published info for missingId
        Catalog mockCatalog = mock(Catalog.class);
        when(mockCatalog.getLayer(missingId)).thenReturn(null);
        when(mockCatalog.getLayerGroup(missingId)).thenReturn(null);

        DefaultTileLayerCatalog catalogWithMock = new DefaultTileLayerCatalog(mockCatalog, resourceLoader, xStream);

        // write a stale tile-layer file referencing missingId
        File file = new File(baseDirectory, "gwc-layers/" + missingId + ".xml");
        FileUtils.writeStringToFile(
                file,
                "<org.geoserver.gwc.layer.GeoServerTileLayerInfoImpl><id>" + missingId
                        + "</id><name>missing</name></org.geoserver.gwc.layer.GeoServerTileLayerInfoImpl>",
                java.nio.charset.StandardCharsets.UTF_8);

        // initialize with the mock catalog; this should skip the file
        catalogWithMock.initialize();

        assertNull(catalogWithMock.getLayerById(missingId));
    }

    private void writeFileLayerInfoImpl(File file, String name) throws IOException {
        FileUtils.writeStringToFile(
                file,
                "<org.geoserver.gwc.layer.GeoServerTileLayerInfoImpl><id>id1</id><name>"
                        + name
                        + "</name></org.geoserver.gwc.layer.GeoServerTileLayerInfoImpl>",
                "UTF-8");
    }

    @Test
    public void testSavedXML() throws IOException, SAXException, XpathException {
        // checking that the persistence looks as expected
        final GeoServerTileLayerInfo original;
        {
            final GeoServerTileLayerInfo info = new GeoServerTileLayerInfoImpl();
            info.setId("id1");
            info.setName("name1");
            info.getMimeFormats().add("image/png");
            info.getMimeFormats().add("image/jpeg");
            info.setCacheWarningSkips(new LinkedHashSet<>(Arrays.asList(WarningType.values())));

            StyleParameterFilter parameterFilter = new StyleParameterFilter();
            parameterFilter.setStyles(Collections.emptySet());
            info.addParameterFilter(parameterFilter);

            assertNull(catalog.save(info));

            original = catalog.getLayerById("id1");
            assertEquals(info.getMimeFormats(), original.getMimeFormats());

            original.getMimeFormats().clear();
            original.getMimeFormats().add("image/gif");
            original.setName("name2");
        }

        catalog.save(original);

        File file = new File(baseDirectory, "gwc-layers/id1.xml");
        String xml = FileUtils.readFileToString(file, StandardCharsets.UTF_8);

        XpathEngine xpath = XMLUnit.newXpathEngine();
        Document doc = XMLUnit.buildControlDocument(xml);
        // no custom attribute for the class, we set a default
        assertEquals("", xpath.evaluate("//cacheWarningSkips/class", doc));
        assertEquals("Default", xpath.evaluate("//cacheWarningSkips/warning[1]", doc));
        assertEquals("Nearest", xpath.evaluate("//cacheWarningSkips/warning[2]", doc));
        assertEquals("FailedNearest", xpath.evaluate("//cacheWarningSkips/warning[3]", doc));
    }
}
