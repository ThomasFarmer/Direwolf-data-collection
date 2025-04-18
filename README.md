# Direwolf-data-collection

### Project description
A small portfolio project showcasing data collection of APRS data packets, hosting it in AWS and visualizing it.

![maponly](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/maponly.png)

**Planned architecture:**

The project aims to simulate the need to do some periodic data collection in an industrial environment. I plan to showcase here some of the basic solutions I've learned while working in such environments. 
For the sake of simplicity I've decided to to use a simple IoT core deployment instead of Greengrass, but if time allows I might create a version of this demo project which relies on that. 

![info](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/df-data-coll-archi.png)

As it is seen on the diagram, the whole project can be separated to three main areas:

**I. Radio-to-PC connection.**
 
This section of the infrastructure is the device which provides us with a relatively continuous stream of data. The radio is connected to a VHF fiberglass pole antenna, which is currently mounted on the balcony. As this location is on a small hill overlooking the Danube and the northern section of the capital, it should give us relatively good coverage in the south / south-east directon where the signal are not blocked by elements of the Pilis mountain range. 
![info](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/radio-antenna.png)

For APRS data traffic, we need to set the radio to **144.800 MHz**, which is the designated frequency for **APRS** data traffic in the European region. The radio is also relaying 
the data stream to the **Digimode USB interface** made by [xggcomms](https://xggcomms.com/). Connecting the device should not be difficult, as it is specifically made to interface this Yeasu radio series. 

Setting up the radio connection:
- Connect the audio jacks to the soundcard's microphone and sound output ports.
- Connect the USB connector to one of the USB ports on the PC, this is how most radio-related software products re able be able to control the radio remotely.
- Connect our CAT serial port to the corresponding port on the back of the radio. This DB-9 connector is used for interconnection to a PC's serial port in order to achieve computer-assisted operation.  
- Connect the PKT jack to the corresponding port on the back of the radio. The PKT or "packet" jack is a 6-pin mini DIN connector which accepts AFSK (Audio Frequency Shift Keying) input, alongside fixed-level receiver audio output, PTT, and ground lines.
- Connect the Data in/out jack to the corresponding port on the back of the radio.This 3.5 mm 3-pin jack provides constant-level receiver audio output on the ring contact, and accepts transmit audio input and PTT on the tip.
- Make sure that the PC has the required [drivers](https://ftdichip.com/drivers/d2xx-drivers/) installed to be able to communicate properly with the USB interface.
![info](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/radio-conn.png)

After establishing the hardware connection, the computer tasked with interpreting digital traffic has to have the some sort of software to do so. In our case, the PC connected to the radio is an old desktop computer currently running Linux Mint. The system has a copy of [Direwolf](https://github.com/wb2osz/direwolf) installed, which is one of the key requirements of this project. Direwolf is a modern, software based TNC (Terminal Node Controller) which allows our APRS packets to be transcribed from analoge sound format into something more comprehensible for our purposes. 
Normally we can connect other APRS monitoring applications through a serial port connection, such as [YAAC](https://www.ka2ddo.org/ka2ddo/YAAC.html) to our running Direwolf instance, but the purpose of this project is to "simulate" data collection from data log collection, so instead of the normal way, our IoT application will monitor the log files produced by direwolf, and we will only use YAAC (or the [aprs.fi](www.aprs.fi) service) to check if the collected data is in fact accurate.


**II. IoT Core deployment.**

The **direwolf_logparser_watchdog** unit will pick up any new entries made by direwolf, and will parse it into a ready-to-send format for the IoT Core deployment, and is relying on a class defined in the **direwolf_logparser_sender** script to communicate with AWS.

The IoT Core deployment section of this project has two main dependencies, which we need to install for this project to be functional:

- The [watchdog](https://pypi.org/project/watchdog/) library for python provides a well-tested solution for monitoring changes in files and directory structures. The **direwolf_logparser_watchdog.py** script relies on this exact library to monitor changes in the direwolf log dumps, where we scan for geographic data, which we plan to display later in our cloud-hosted map application. 
- The [awsiotsdk](https://pypi.org/project/awsiotsdk/) library handles the communication between out IoT Core deployment, and AWS. For this, we need to create, activate and download a certificate bundle. The  **direwolf_logparser_sender.py** script looks up the path for these certificate files from environment variables, which can be set up manually, or by editing the .bashrc file. 
These are the following:

The IoT endpoint is an account level url, which allow us to communicate with IoT Core. The expected value of the variable should look something like this: <br/> **DF_COLLECTOR_IOT_ENDPOINT** - xxxxxxxxxxxxxx-ats.iot.eu-central-1.amazonaws.com

The thing name we use in our deployment. The default value for this project is the following: <br/> **DF_COLLECTOR_CLIENT_ID** - dwc_poc_data_collection_thing

The certificate bundle AWS provides us consists of 5 files, 3 of which we need to refer in the following environment variables for the data upload to function. These are the certificate.pem.crt file, the private.pem.key file, and the root certificate. <br/> **DF_COLLECTOR_CERT_PATH** - xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-certificate.pem.crt <br/> **DF_COLLECTOR_PRIVATE_KEY** - xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-private.pem.key <br/> **DF_COLLECTOR_ROOT_CA** - AmazonRootCA1.pem

The certificate folder tells our script where our certificates are stored. Default value is /certs, but it can be anything, this value will be evaulated by the python's os.path.join function later in the code.
**DF_COLLECTOR_CERT_FOLDER** - ./certs

And finally we need to tell the software where direwolf dumps its log files. This is entirely up to the user, as this value is set in the direwolf config file. <br/> 
**DF_LOG_PATH** - /home/someuser/direwolf-logs

The two external dependency libraries are mentioned in the attached requirements.txt file. 

To run the module, we just simply need to call **python3 direwolf_logparser_watchdog.py**. 

![log](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/iot_log_example.png)
        
**III. Cloud-hosted infrastructure.**

The two lambda functions hosted in AWS also require a few specific libraries.
First, both functions rely heavily on the functionality provided by the [boto3](https://pypi.org/project/boto3/) library, however this one is included by default for all lambda functions (we only need to install this library if we're using it outside of the lambda environments).
On top of that, the second function, the **aprs-map** function is a simple [flask](https://flask.palletsprojects.com/en/stable/) application, which relies on the [awsgi](https://github.com/slank/awsgi) library in order for it to be able to be hosted as a lambda function. Both of these libraries can be found in form of zip files, prepared to be deployed as layers in this repository. We'll talk more about it, as we discuss the contents of the cloudformation templates.

***Deployment:***
The cloudformation template package is divided into 4 parts, and they should be deployed in the following order:
1.  [Policies](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-01-policies.yaml). 
2. [Callsign data updater function, plus the Callsign data DynamoDB table](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-02-lambda-to-dynamo.yaml)
3. [IoT Core deployment](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-03-iot.yaml)
4. [APRS Map function](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-04-lambda-to-map.yaml)
<br/>



**1. The policy template** --> [Link to template](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-01-policies.yaml). 
<br/>
**IAMRoleCallsigndataUpdaterRoleForDirewolf**: This is the Lambda role used by both lambda functions. It is a loose policy, allowing for most DynamoDB-related actions to be performed on one given table.

**IoTPolicyForDireWolf**: This is also a loosely defined IoT policy used by the project. Normally it is advised to use this to restrict access, but due to of time constrains, I did not introduce any restrictions here.



**2.  Callsign data updater and DynamoDB table** --> [Link to template](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-02-lambda-to-dynamo.yaml). 
<br/>
**LambdaFunctionCallsigndataupdater**: This function is responsible for catching any incoming MQTT messages, and dumping it in the DynamoDB table. It has no other purpose then to fill up the table with any data which triggers it, which means that I've decided to keep it as part of the template for easier deployment, since the whole thing can be written down on a napkin anyway. The only library it requires besides some base python ones is the above mentioned [boto3](https://pypi.org/project/boto3/), which is available by default.

**DynamoDBTableCallsigndata**: This table stores our callsign and location data. Any APRS packet which reaches our antenna (and we're able to decode it) gets added to this database. To avoid duplicate entries, the callsign is used as the index, so ham operators on the move get their data constantly updated. 

![table](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/dynamo_table_items.png)

**3. IoT Core deployment** --> [Link to template](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-03-iot.yaml)
<br/>
**DirewolfDataCollectionIoTTopicRule**: This is the IoT Topic rule we use to monitor data appearing on the "aprs/geojson" topic, and feed it to the Callsign data updated function.

**DirewolfDataCollectionThing**: This is the IoT Thing we have in our stack, which is the client device of the local deployment from AWS-s perspective. It's purpose is to be the extension of the AWS cloud on our local computer, and collect data in various manners - through our **direwolf_logparser_watchdog** and **direwolf_logparser_sender** scripts in this case, as they are authenticated to talk to AWS in the "thing's name". 

**LambdaPermissionFunctioncallsigndataupdater**: The lambda permission is the link between our IoT rule and the lambda itself. Whenever data appears on the topic, and the rule gets triggered, only with this permission present can the lambda get the trigger event.  

![mqtt](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/iot_mqtt_test.png)

**4. APRS Map function** --> [Link to template](https://github.com/ThomasFarmer/Direwolf-data-collection/blob/main/cf/dwc-04-lambda-to-map.yaml) 
**AprsMapLambdaLayerFlask**: This is the lambda layer containing Flask. It requires an S3 bucket and the S3 key (zipfile name) as a parameter.
**AprsMapLambdaLayerAwsgi**: This is the lambda layer containing aws-gi. It requires an S3 bucket and the S3 key (zipfile name) as a parameter.
**AprsMapLambdaFunction**: This is our flask application hosting the map. The map itself is using leaflet.js and jquery to operate. Source code and a compressed zip file version of the function can be found here: [Link to folder](https://github.com/ThomasFarmer/Direwolf-data-collection/tree/main/aprs-map).
**AprsMapPermissionForURL**: In order to have access to the lambda URL, we need to set up a permission first. 
**AprsMapLambdaUrl**: This will be the link we can use to see our leaflet map hosted by the flask application. This link can be found in AWS's management console next to the lambda function.

![lambdaurl](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/lambda_url.png)

### Usage and notes

After this lengthy setup process, we can finally start gathering data.
To quickly summarize how to start the project:
- Turn on the radio, make sure it's on 144.800 MHz,
- Start Direwolf, make sure we're monitoring it's log folder,
- Start the direwolf_logparser_watchdog script, make sure the certificates and the environment variables are all set,
- Acquire the Lambda URL by checking our APRS Map lambda in the management console, or use the aws cli tool to query the exported value of the APRS map stack (or the URL itself directly).
- Visit the link in a browser, and wait for the data to be populated. The map refreshes its content every 5 seconds, so we should get some data relatively quickly. 

***Notes:*** *The map application is very rudimentary, so unlike in other, full-fledged APRS applications there is no way to trace movement, or do queries or anything.* 

*The map also disregards time, so any marker represents the last known location of the amateurs heard. They can be outside of our hearing range or stopped broadcasting.*

![map](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/aprs_map_screenshot.png)







