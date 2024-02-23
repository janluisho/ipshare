"""
IpShare uses the IP2Location LITE database for <a href="https://lite.ip2location.com">IP geolocation</a>.
"""
import os
import csv
import asyncio
import aiofiles
import aiohttp
import config
import requests

from typing import List
from app import app, db
from datetime import date
from zipfile import ZipFile
from tqdm import tqdm
from tqdm.asyncio import tqdm as aiotqdm
from bs4 import BeautifulSoup


async def fetch_img(session: aiohttp.ClientSession, url: str, path: str) -> None:
    async with session.get(url) as response:
        if response.status == 200:
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await response.read())
                await f.close()
        else:
            print(f"couldn't fetch {url} {response.status}")


async def get_country_images() -> None:
    result = requests.get("https://de.wikipedia.org/wiki/ISO-3166-1-Kodierliste")
    assert result.status_code == 200
    soup = BeautifulSoup(result.text, 'html.parser')

    async with aiohttp.ClientSession() as session:
        tasks = []
        for img in soup.find_all("table")[2].find_all("img", {"class": "mw-file-element"}):
            url = f'https:{img["src"].replace("20px", "40px")}'
            path = f'D:/Python/ipshare/app/static/flags/{img.find_parent("tr").find_all("td")[1].text[:2]}.png'
            tasks.append(fetch_img(session, url, path))

        for f in aiotqdm.as_completed(tasks, unit="images", desc=f"Downloading country images"):
            await f


class Country(db.Model):
    code: db.Mapped[str] = db.mapped_column(db.CHAR(2), primary_key=True, nullable=False)  # Zweistelliger Ländercode basierend auf ISO 3166.
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(64), unique=True, nullable=True)  # Ländername basierend auf ISO 3166.
    display: db.Mapped[str] = db.mapped_column(db.String(48), nullable=False)
    regions: db.Mapped[List["Region"]] = db.relationship(cascade="all, delete-orphan")


class Region(db.Model):
    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True, nullable=False)
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(128), nullable=True)  # Name der Region oder des Bundesstaates.
    country: db.Mapped[str] = db.mapped_column(db.CHAR(2), db.ForeignKey('country.code', ondelete='CASCADE'))
    citys: db.Mapped[List["City"]] = db.relationship(cascade="all, delete-orphan")


class City(db.Model):
    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True, nullable=False)
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(128), nullable=True)  # Stadtname.
    region: db.Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey("region.id", ondelete='CASCADE'))
    segments: db.Mapped[List["IpSegment"]] = db.relationship(cascade="all, delete-orphan")


class IpSegment(db.Model):
    ip_from: db.Mapped[int] = db.mapped_column(db.DECIMAL(39, 0), primary_key=True)  # Erste IP-Adresse des Segments.
    ip_to: db.Mapped[int] = db.mapped_column(db.DECIMAL(39, 0), unique=True)  # Letzte IP-Adresse des Segments.
    city: db.Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey("city.id", ondelete='CASCADE'))


def download_db(zip_filename):
    with requests.get(download, stream=True) as response:
        if response.status_code != 200:
            print(f"Error downloading {download}. Status code: {response.status_code}")
        else:
            with open(zip_filename, mode="wb") as file:
                for chunk in tqdm(response.iter_content(chunk_size=1024), unit="kB", desc=f"Downloading {zip_filename}"):
                    file.write(chunk)


def extract_zip(zip_filename: str, filename: str):
    with ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(filename)


def fill_db(filename: str):
    with app.app_context():
        db.create_all()
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            with tqdm(total=4294967295, unit="ip", desc=f"Filling IpSegment into the DB") as pbar:
                for row in spamreader:
                    ip_from, ip_to, country_code, country_name, region_name, city_name = row

                    # replace "-" with None
                    country_name = None if country_name == "-" else country_name
                    region_name = None if region_name == "-" else region_name
                    city_name = None if city_name == "-" else city_name

                    try:
                        ip_from = int(ip_from)
                        ip_to = int(ip_to)
                    except ValueError:
                        print(f"Couldn't convert {ip_from} or {ip_to} to int.")
                        exit(-1)
                        continue

                    country = Country.query.filter_by(code=country_code).first()
                    if country is None:
                        # create Country
                        if country_code != "-":
                            display = f"static/flags/{country_code}.png"
                            assert os.path.exists("app/" + display), display
                        else:
                            display = "-"

                        country = Country(code=country_code, name=country_name, display=display)
                        db.session.add(country)
                        db.session.commit()

                    region = Region.query.filter_by(name=region_name, country=country.code).first()
                    if region is None:
                        # create Region
                        region = Region(name=region_name, country=country.code)
                        db.session.add(region)
                        db.session.commit()

                    city = City.query.filter_by(name=city_name, region=region.id).first()
                    if city is None:
                        # create City
                        city = City(name=city_name, region=region.id)
                        db.session.add(city)
                        db.session.commit()

                    # add the IP segment
                    segment = IpSegment(ip_from=ip_from, ip_to=ip_to, city=city.id)
                    db.session.add(segment)
                    pbar.update(ip_to - ip_from)
                db.session.commit()


if __name__ == "__main__":
    DATABASE_CODE = "DB3LITECSV"  # Don't forget to change file_name when changing this.
    download = f"https://www.ip2location.com/download/?token={config.IP2LOCATION_TOKEN}&file={DATABASE_CODE}"
    zip_filename = f"{DATABASE_CODE}-{date.today()}.zip"
    dirname = f"IP2LOCATION/{DATABASE_CODE}-{date.today()}"
    file_name = "IP2LOCATION-LITE-DB3.CSV"  # depends on DATABASE_CODE

    asyncio.run(get_country_images())
    download_db(zip_filename)

    try:
       os.mkdir(dirname)
    except FileExistsError:
       pass
    print(f"Extracting {zip_filename} to {dirname} ...")
    extract_zip(zip_filename, dirname)
    #os.remove(zip_filename)

    with app.app_context():
        try:
            num_rows_deleted = db.session.query(IpSegment).delete()
            if num_rows_deleted > 0:
                print("The IpSegment table is not empty.\nIf your updating the DB you will need to delete all rows.")
                confirm = input(f"Are you sure you want to delete {num_rows_deleted} rows? (y/n)")
                while confirm not in ["y", "n"]:
                    print("Please enter y or n")
                    confirm = input("Are you sure you want to delete all rows? (y/n)")
                if confirm == "y":
                    db.session.commit()
                    print("IpSegment table cleared.\nProceeding to fill the DB with new data...")
                else:
                    db.session.rollback()
                    print("DB not updated.")
                    exit()
        except Exception as e:
            if "no such table: ip_segment" not in str(e):
                db.session.rollback()
                print(f"Ups something went wrong: {e}")
                exit(-1)

    fill_db(f"{dirname}/{file_name}")

