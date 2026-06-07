package org.geoserver.web.evaluate;

import java.util.Properties;
import org.apache.wicket.ajax.AjaxRequestTarget;
import org.apache.wicket.ajax.markup.html.form.AjaxButton;
import org.apache.wicket.markup.head.CssHeaderItem;
import org.apache.wicket.markup.head.IHeaderResponse;
import org.apache.wicket.markup.html.WebMarkupContainer;
import org.apache.wicket.markup.html.basic.Label;
import org.apache.wicket.markup.html.form.Form;
import org.apache.wicket.markup.html.form.TextField;
import org.apache.wicket.model.Model;
import org.geoserver.platform.GeoServerEnvironment;
import org.geoserver.platform.GeoServerExtensions;
import org.geoserver.web.GeoServerSecuredPage;
import org.springframework.beans.factory.config.PlaceholderConfigurerSupport;
import org.springframework.util.PropertyPlaceholderHelper;
import org.springframework.util.PropertyPlaceholderHelper.PlaceholderResolver;

public class PageEvaluateVariables extends GeoServerSecuredPage {

    private static final String DEFAULT_PREFIX = PlaceholderConfigurerSupport.DEFAULT_PLACEHOLDER_PREFIX;
    private static final String DEFAULT_SUFFIX = PlaceholderConfigurerSupport.DEFAULT_PLACEHOLDER_SUFFIX;
    private static final String DEFAULT_SEPARATOR = PlaceholderConfigurerSupport.DEFAULT_VALUE_SEPARATOR;
    private static final String DEFAULT_PROPERTIES_FILE = "geoserver-environment.properties";

    private Model<String> inputModel = Model.of("");
    private Model<String> resultModel = Model.of("");
    private Model<String> propertiesFileModel = Model.of("");

    public PageEvaluateVariables() {
        // Determine which properties file is being used
        String envPropertiesPath = GeoServerExtensions.getProperty("ENV_PROPERTIES");
        String propertiesFileInfo;
        if (envPropertiesPath != null && !envPropertiesPath.isEmpty()) {
            propertiesFileInfo = "Using properties file: " + envPropertiesPath;
        } else {
            propertiesFileInfo =
                    "Using default properties file: " + DEFAULT_PROPERTIES_FILE + " (in GeoServer data directory)";
        }
        propertiesFileModel.setObject(propertiesFileInfo);

        // Add properties file info label
        Label propertiesFileLabel = new Label("propertiesFile", propertiesFileModel);
        add(propertiesFileLabel);

        // Create a form
        Form<Void> form = new Form<>("form");
        add(form);

        // Add input container
        WebMarkupContainer inputContainer = new WebMarkupContainer("inputContainer");
        form.add(inputContainer);

        // Add label
        Label inputLabel = new Label("inputLabel", "Enter text with placeholders:");
        inputContainer.add(inputLabel);

        // Add text input field
        TextField<String> inputField = new TextField<>("input", inputModel);
        inputField.setOutputMarkupId(true);
        inputContainer.add(inputField);

        // Add button container
        WebMarkupContainer buttonContainer = new WebMarkupContainer("buttonContainer");
        form.add(buttonContainer);

        // Add result container (must be created before button references it)
        WebMarkupContainer resultContainer = new WebMarkupContainer("resultContainer");
        add(resultContainer);

        // Add result label (must be created before button references it)
        Label resultLabel = new Label("result", resultModel);
        resultLabel.setOutputMarkupId(true);
        resultContainer.add(resultLabel);

        // Add Ajax submit button
        AjaxButton submitButton = new AjaxButton("submit") {
            @Override
            protected void onSubmit(AjaxRequestTarget target) {
                // Get the input
                String input = inputModel.getObject();
                String result;

                if (input == null || input.trim().isEmpty()) {
                    result = "Please enter a value to evaluate";
                } else {
                    // Check if environment parametrization is enabled
                    if (!GeoServerEnvironment.allowEnvParametrization()) {
                        result =
                                "Environment parametrization is disabled. Set ALLOW_ENV_PARAMETRIZATION=true to enable.";
                    } else {
                        // Evaluate the input using ONLY the properties file
                        try {
                            GeoServerEnvironment geoServerEnv = GeoServerExtensions.bean(GeoServerEnvironment.class);
                            Properties props = geoServerEnv.getProps();

                            if (props == null || props.isEmpty()) {
                                result =
                                        "No properties file loaded. Ensure geoserver-environment.properties exists or ENV_PROPERTIES is set.";
                            } else {
                                // Create a resolver that only uses the properties file
                                PlaceholderResolver resolver = placeholder -> props.getProperty(placeholder);
                                PropertyPlaceholderHelper helper = new PropertyPlaceholderHelper(
                                        DEFAULT_PREFIX, DEFAULT_SUFFIX, DEFAULT_SEPARATOR, true);

                                String evaluated = helper.replacePlaceholders(input, resolver);
                                result = evaluated;
                            }
                        } catch (Exception e) {
                            result = "Error evaluating: " + e.getMessage();
                        }
                    }
                }

                resultModel.setObject(result);

                // Update the result label via Ajax
                target.add(resultLabel);
            }
        };
        buttonContainer.add(submitButton);
    }

    @Override
    public void renderHead(IHeaderResponse response) {
        super.renderHead(response);
        // Content-Security-Policy: inline styles must have nonce
        String css =
                """
                .eval-input-container {
                    margin: 0 0 0.5em;
                }
                .eval-input-label {
                    display: block;
                    padding: 0 0 1px;
                    line-height: 1.5em;
                }
                .eval-input-field {
                    color: #333;
                    font-size: 1em;
                    margin: 0.5em 0;
                    border: 1px solid #bbb;
                    border-color: #7c7c7c #c3c3c3 #ddd;
                    padding: 5px;
                }
                .eval-button-container {
                    margin: 0.5em 0;
                }
                .eval-submit-button {
                    background: var(--gs-green-light) url(../img/button-gradient.png) top left repeat-x;
                    border: 1px solid var(--gs-green-light);
                    font-size: 0.9em;
                    font-weight: bold;
                    text-decoration: none;
                    color: var(--gs-blue);
                    cursor: pointer;
                    padding: 5px 10px 5px 7px;
                    -moz-border-radius: 5px;
                    -webkit-border-radius: 5px;
                    border-radius: 5px;
                    line-height: 1.5;
                    font-family: Tahoma, Arial, sans-serif;
                }
                .eval-submit-button:hover {
                    background-color: var(--gs-green-dark);
                }
                .eval-result-container {
                    padding: 0.5em;
                    margin-top: 0.5em;
                    background-color: #d9edf7;
                    border: 1px solid #bce8f1;
                    border-radius: 3px;
                }\
                """;
        response.render(CssHeaderItem.forCSS(css, "org-geoserver-web-evaluate-PageEvaluateVariables"));
    }
}
