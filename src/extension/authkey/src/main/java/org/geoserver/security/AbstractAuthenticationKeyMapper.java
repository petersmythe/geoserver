/* (c) 2014 Open Source Geospatial Foundation - all rights reserved
 * (c) 2012 - 2013 OpenPlans
 * This code is licensed under the GPL 2.0 license, available at the root
 * application directory.
 */
package org.geoserver.security;

import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.logging.Logger;
import org.geoserver.security.validation.FilterConfigException;
import org.springframework.util.StringUtils;

/**
 * Base class for {@link AuthenticationKeyMapper} implementations
 *
 * @author christian
 */
public abstract class AbstractAuthenticationKeyMapper implements AuthenticationKeyMapper {

    protected static Logger LOGGER =
            org.geotools.util.logging.Logging.getLogger("org.geoserver.security");

    private String beanName;
    private String userGroupServiceName;
    private String authenticationFilterName;
    private GeoServerSecurityManager securityManager;

    private Map<String, String> parameters = new HashMap<>();

    public AbstractAuthenticationKeyMapper() {
        super();
        fillDefaultParameters();
    }

    @Override
    public void setBeanName(String name) {
        beanName = name;
    }

    @Override
    public String getBeanName() {
        return beanName;
    }

    @Override
    public String getUserGroupServiceName() {
        return userGroupServiceName;
    }

    @Override
    public void setUserGroupServiceName(String userGroupServiceName) {
        this.userGroupServiceName = userGroupServiceName;
    }

    @Override
    public GeoServerSecurityManager getSecurityManager() {
        return securityManager;
    }

    @Override
    public void setSecurityManager(GeoServerSecurityManager securityManager) {
        this.securityManager = securityManager;
    }

    protected GeoServerUserGroupService getUserGroupService() throws IOException {
        GeoServerUserGroupService service =
                getSecurityManager().loadUserGroupService(getUserGroupServiceName());
        if (service == null) {
            throw new IOException("Unkown user/group service: " + getUserGroupServiceName());
        }
        return service;
    }

    protected void checkProperties() throws IOException {
        if (StringUtils.hasLength(getUserGroupServiceName()) == false) {
            throw new IOException("User/Group Service Name is unset");
        }
        if (getSecurityManager() == null) {
            throw new IOException("Security manager is unset");
        }
    }

    protected String createAuthKey() {
        return UUID.randomUUID().toString();
    }

    /** Returns the list of configuration parameters supported by the mapper. */
    @Override
    public Set<String> getAvailableParameters() {
        return new HashSet<>();
    }

    /**
     * Configures the mapper parameters.
     *
     * @param parameters mapper parameters
     */
    @Override
    public void configureMapper(Map<String, String> parameters) {
        this.parameters = parameters;
        fillDefaultParameters();
    }

    /** Fills parameters with default values (if defined by the mapper. */
    private void fillDefaultParameters() {
        for (String paramName : getAvailableParameters()) {
            if (!this.parameters.containsKey(paramName)) {
                this.parameters.put(paramName, getDefaultParamValue(paramName));
            }
        }
    }

    /**
     * Gets the default value for the given parameter. Default implementation always returns an
     * empty string.
     */
    protected String getDefaultParamValue(String paramName) {
        return "";
    }

    @Override
    public Map<String, String> getMapperConfiguration() {
        return parameters;
    }

    /** Validates the given parameter (used by the filter validator). */
    @Override
    public void validateParameter(String paramName, String value) throws FilterConfigException {}

    /** Creates a validation exception (used by inheriting mappers). */
    protected AuthenticationKeyFilterConfigException createFilterException(
            String errorid, Object... args) {
        return new AuthenticationKeyFilterConfigException(errorid, args);
    }

    /** Get the belonging Auth Filter Name to allow the Mapper accessing the auth cache * */
    public String getAuthenticationFilterName() {
        return authenticationFilterName;
    }

    /** Set the belonging Auth Filter Name to allow the Mapper accessing the auth cache * */
    @Override
    public void setAuthenticationFilterName(String authenticationFilterName) {
        this.authenticationFilterName = authenticationFilterName;
    }
}
