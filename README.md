<h2 align="center">UDP Honeypot</h2>
<h3 align="center"><a href="http://83.168.107.114:8000/">Live honeypot data</a></h3><br>


## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Authors](#authors)

## About <a name = "about"></a>

At the beginning of creating that project my motivation was to collet as many botnet samples as possible to analyze their techniques of evading anti viruses. Shortly after finishing main stage I realized that I could gather even more data and so I expanded that into current form of the project where it also collects UDP packets data. Script has built-in dictionairy which stores well known UDP payloads. By this approach we can identify some of the received payloads, however still most of them are unknown to me. What's most important that honeypot can help you find new amplification vectors,refinded payloads and other useful informations like IP addresses that are used for scanning networks.

## 🏁 Getting Started <a name = "getting_started"></a>

### Prerequisites

```
Python 3.8 or higher
PostgreSQL database
```

### Installing

At first clone this repository using:
```
git clone https://github.com/OpsecGuy/Project-Honeypot.git
```

If you already have Python installed execute that command in project folder:
```
pip install -r requirements.txt
```

Once you do it all what left to do is to setup PostgreSQL database. You can find DDL below and import that into your database:
```
-- public."data" definition

-- Drop table

-- DROP TABLE public."data";

CREATE TABLE public."data" (
	id int4 NULL,
	ipaddr varchar(50) NULL,
	port int4 NULL,
	protocol varchar(50) NULL,
	payload varchar(4096) NULL,
	server varchar(50) NULL,
	creation_date float4 NULL,
	protocol_type varchar(50) NULL,
	is_botnet bool NULL
);


-- public.protocols definition

-- Drop table

-- DROP TABLE public.protocols;

CREATE TABLE public.protocols (
	id int4 NULL,
	name varchar(50) NULL,
	count int4 NULL,
	port int4 NULL,
	protocol_type varchar(50) NULL
);
```

## 🎈 Usage <a name="usage"></a>
You can run honepot using that command:
```python3 app.py```

On first run ```config.json``` file will be created. Inside that file declare database connection informations and restart script.


## ✍️ Authors <a name = "authors"></a>
- [@OpsecGuy](https://github.com/OpsecGuy) - Idea & Initial work
- [@Phenomite](https://github.com/Phenomite/AMP-Research/) - Inspiration

