# A Remote "Gdal Contour" Process Binding Example

Before continue reading this section, please be sure to have fully understood and successfully completed all the passages at sections:

- `extensions_wps_remote_install_geoserver`
- `extensions_wps_remote_install_xmpp`
- `extensions_wps_remote_install_python`

## Running the Python WPS Agent

In order to start the RemoteWPS Python Wrapper, we need to run an instance of the `wpsagent.py` using the configuration files defined at section `extensions_wps_remote_install_python`

``` bash
$> cd C:\work\RemoteWPS

$> python wpsagent.py -r .\xmpp_data\configs\remote.config -s .\xmpp_data\configs\myservice\service.config service
```

Few instants after the execution of the command, you should be able to see con `invite` message on the prompt

<figure class="align-center">
<img src="images/run_example001.jpg" />
</figure>

and the `default.GdalContour` instance successfully connected and authenticated into the XMPP Server channels

<figure class="align-center">
<img src="images/run_example002.jpg" />
</figure>

<figure class="align-center">
<img src="images/run_example003.jpg" />
</figure>

The new GeoServer WPS Process should be now available among the GeoServer Processes

<figure class="align-center">
<img src="images/run_example004.jpg" />
</figure>

The GeoServer Remote Process Factory automatically creates the WPS interface for the new process, exposing through the OGC WPS Protocol the Inputs and Outputs definitions like shown in the illustration below

<figure class="align-center">
<img src="images/run_example005.jpg" />
</figure>

At the Execute Request the Remote WPS Python framework starts a new thread and assigns to it the unique **execution_id** provided by GeoServer.

<figure class="align-center">
<img src="images/run_example006.jpg" />
</figure>

The logs of the execution are stored into the **working directory**

<figure class="align-center">
<img src="images/run_example007.jpg" />
</figure>

From the log file is possible to recognize the full command line executed by the Remote WPS Python wrapper along with the lines received through the standard output

<figure class="align-center">
<img src="images/run_example008.jpg" />
</figure>

The main window shows the received XMPP messages and the actions taken accordingly

<figure class="align-center">
<img src="images/run_example009.jpg" />
</figure>

> [!NOTE]
> The same information can be found into the log file specified into the “logger.properties” file (see above).

On GeoServer side, it is possible to follow the process execution by following the messages sent via XMPP to the GeoServer logs

``` bash
$> tail -F -n 200 /storage/data/logs/geoserver.log
```

<figure class="align-center">
<img src="images/run_example010.jpg" />
</figure>
