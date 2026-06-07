package org.geoserver.web.evaluate;

import org.geoserver.web.GeoServerWicketTestSupport;
import org.geoserver.web.ToolPage;
import org.junit.Test;

public class PageEvaluateVariablesTest extends GeoServerWicketTestSupport {

    @Test
    public void testToolsMenuContainsEvaluateVariables() {
        // log in as admin
        login();

        // start the Tools page
        tester.startPage(ToolPage.class);
        tester.assertRenderedPage(ToolPage.class);

        // find the label component that displays our i18n title (search by rendered content)
        org.apache.wicket.Component titleLabel = findComponentByContent(
                tester.getLastRenderedPage(), "Evaluate Variables", org.apache.wicket.markup.html.basic.Label.class);
        org.junit.Assert.assertNotNull("Evaluate Variables link title should be present in the Tools list", titleLabel);

        // get the link path - the title is nested inside theLink component
        String titlePath = titleLabel.getPageRelativePath();
        // title path looks like toolList:NN:theLink:theTitle
        // we need to click the theLink component, so remove the :theTitle part
        String linkPath = titlePath.substring(0, titlePath.lastIndexOf(':'));

        tester.clickLink(linkPath); // ensure our page renders and contains the expected label
        tester.assertRenderedPage(PageEvaluateVariables.class);
        tester.assertLabel("title", "Evaluate Variables");
    }
}
