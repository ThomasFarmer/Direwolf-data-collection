# Direwolf-data-collection

### Project description
A small portfolio project showcasing data collection of APRS data packets, hosting it in AWS and visualizing it.

**Planned architecture:**

The project aims to simulate the need to do some periodic data collection in an industrial environment. I plan to showcase here some of the basic solutions I've learned while working in such environments. 
For the sake of simplicity I've decided to to use a simple IoT core deployment instead of Greengrass, but if time allows I might create a version of this demo project which relies on that. 

![info](https://raw.githubusercontent.com/ThomasFarmer/Direwolf-data-collection/refs/heads/main/doc/df-data-coll-archi.png)

As it is seen on the diagram, the whole project can be separated to three main areas:

**I. Radio-to-PC connection.**
 
This section of the infrastructure is the device which provides us with a relatively continuous stream of data. One of the radios I own is an old **Yaesu FT-847** which I've inherited from HA7WJ *(SK)*. The radio is connected to a VHF fiberglass pole antenna, which is currently mounted on the balcony. 

I've set the radio to send and recieve on **144.800 MHz**, which is the designated frequency for **APRS** data traffic in the European region. The radio is also relaying 
the data stream to the **Digimode USB interface** made by [xggcomms](https://xggcomms.com/).

The PC connected to the radio is an old desktop computer currently running Linux Mint. The system has a copy of  [Direwolf](https://github.com/wb2osz/direwolf) installed, which is one of the key requirements of this project. 

**II. IoT Core deployment.**

The **direwolf_logparser_watchdog** unit will pick up any new entries made by direwolf, and will parse it into a ready-to-send format for the IoT Core deployment.

*TBD...*

**III. Cloud-hosted infrastructure.**

*TBD...*

### Step-by-step installation

*TBD...*

### Usage and screenshots

*TBD...*