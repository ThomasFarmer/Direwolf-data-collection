# Direwolf-data-collection

### Project description
A small portfolio project showcasing data collection of APRS data packets, hosting it in AWS and visualizing it.

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
- Connect our CAT serial port to the corresponding port on the back of the radio. 
- Connect the PKT jack to the corresponding port on the back of the radio.
- Connect the Data in/out jack to the corresponding port on the back of the radio.
- Make sure that the PC has the required [drivers](https://ftdichip.com/drivers/d2xx-drivers/) installed to be able to communicate properly with the USB interface.
![info](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/radio-conn.png)

After establishing the hardware connection, the computer tasked with interpreting digital traffic has to have the some sort of software to do so. In our case, the PC connected to the radio is an old desktop computer currently running Linux Mint. The system has a copy of [Direwolf](https://github.com/wb2osz/direwolf) installed, which is one of the key requirements of this project. Direwolf is a modern, software based TNC (Terminal Node Controller) which allows our APRS packets to be transcribed from analoge sound format into something more comprehensible for our purposes. 
Normally we can connect other APRS monitoring applications through a serial port connection, such as [YAAC](https://www.ka2ddo.org/ka2ddo/YAAC.html) to our running Direwolf instance, but the purpose of this project is to "simulate" data collection from data log collection, so instead of the normal way, our IoT application will monitor the log files produced by direwolf, and we will only use YAAC (or the [aprs.fi](www.aprs.fi) service) to check if the collected data is in fact accurate.



**II. IoT Core deployment.**

The **direwolf_logparser_watchdog** unit will pick up any new entries made by direwolf, and will parse it into a ready-to-send format for the IoT Core deployment.

*TBD...*

**III. Cloud-hosted infrastructure.**

*TBD...*

### Step-by-step installation

*TBD...*

### Usage and screenshots

*TBD...*