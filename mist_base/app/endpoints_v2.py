from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity, JWTError
from mist_main import return_app
from common.models import main, base_model
from common.db_helpers import PasswordCheck
import re
import hashlib
from werkzeug.utils import secure_filename
import base64
import os
from datetime import datetime, timedelta
import calendar
from socket import inet_aton, inet_ntoa
import netaddr
import json
import subprocess

import os

api_endpoints = Blueprint('mist_auth', __name__, url_prefix="/api/v2")
api = Api(api_endpoints)
this_app = return_app()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in this_app.config['ALLOWED_EXTENSIONS']

def rs_users():
    return main.session.query(main.MistUser).join(main.UserPermission, main.MistUser.permission_id == main.UserPermission.id)

def rs_user_access():
    return main.session.query(main.UserAccess)

def rs_request_user_access():
    return main.session.query(main.requestUserAccess)

def rs_repos():
    return main.session.query(main.Repos)

def rs_security_centers():
    return main.session.query(main.SecurityCenter)

def rs_banner_text():
    return main.session.query(main.BannerText)

def rs_classification():
    return main.session.query(main.Classifications)

def rs_mist_params():
    return main.session.query(main.MistParams)

def rs_tag_definitions():
    return main.session.query(main.TagDefinitions)

def rs_publish_sites():
    return main.session.query(main.PublishSites)

def rs_tags():
    return main.session.query(main.Tags)

def rs_tagged_repos():
    return main.session.query(main.TaggedRepos)

def rs_assets():
    return main.session.query(main.Assets)

def rs_tagged_assets():
    return main.session.query(main.TaggedAssets)

def rs_publish_sched():
    return main.session.query(main.PublishSched)

def rs_repo_publish_times():
    return main.session.query(main.RepoPublishTimes)

def rs_publish_jobs():
    return main.session.query(main.PublishJobs)

def rs_repo_publish_times():
    return main.session.query(main.RepoPublishTimes)

def rs_removed_scs():
    return main.session.query(main.RemovedSCs)

# http://stackoverflow.com/a/1960546/6554056
def row_to_dict(row):
    d = {}
    if (row is not None):
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))
    return d

def write_crontab():
    _timezones_json = '[{"value":"Dateline Standard Time","abbr":"DST","offset":-12,"isdst":false,"text":"(UTC-12:00) International Date Line West","utc":["Etc/GMT+12"]},{"value":"UTC-11","abbr":"U","offset":-11,"isdst":false,"text":"(UTC-11:00) Coordinated Universal Time-11","utc":["Etc/GMT+11","Pacific/Midway","Pacific/Niue","Pacific/Pago_Pago"]},{"value":"Hawaiian Standard Time","abbr":"HST","offset":-10,"isdst":false,"text":"(UTC-10:00) Hawaii","utc":["Etc/GMT+10","Pacific/Honolulu","Pacific/Johnston","Pacific/Rarotonga","Pacific/Tahiti"]},{"value":"Alaskan Standard Time","abbr":"AKDT","offset":-8,"isdst":true,"text":"(UTC-09:00) Alaska","utc":["America/Anchorage","America/Juneau","America/Nome","America/Sitka","America/Yakutat"]},{"value":"Pacific Standard Time (Mexico)","abbr":"PDT","offset":-7,"isdst":true,"text":"(UTC-08:00) Baja California","utc":["America/Santa_Isabel"]},{"value":"Pacific Standard Time","abbr":"PDT","offset":-7,"isdst":true,"text":"(UTC-08:00) Pacific Time (US & Canada)","utc":["America/Dawson","America/Los_Angeles","America/Tijuana","America/Vancouver","America/Whitehorse","PST8PDT"]},{"value":"US Mountain Standard Time","abbr":"UMST","offset":-7,"isdst":false,"text":"(UTC-07:00) Arizona","utc":["America/Creston","America/Dawson_Creek","America/Hermosillo","America/Phoenix","Etc/GMT+7"]},{"value":"Mountain Standard Time (Mexico)","abbr":"MDT","offset":-6,"isdst":true,"text":"(UTC-07:00) Chihuahua, La Paz, Mazatlan","utc":["America/Chihuahua","America/Mazatlan"]},{"value":"Mountain Standard Time","abbr":"MDT","offset":-6,"isdst":true,"text":"(UTC-07:00) Mountain Time (US & Canada)","utc":["America/Boise","America/Cambridge_Bay","America/Denver","America/Edmonton","America/Inuvik","America/Ojinaga","America/Yellowknife","MST7MDT"]},{"value":"Central America Standard Time","abbr":"CAST","offset":-6,"isdst":false,"text":"(UTC-06:00) Central America","utc":["America/Belize","America/Costa_Rica","America/El_Salvador","America/Guatemala","America/Managua","America/Tegucigalpa","Etc/GMT+6","Pacific/Galapagos"]},{"value":"Central Standard Time","abbr":"CDT","offset":-5,"isdst":true,"text":"(UTC-06:00) Central Time (US & Canada)","utc":["America/Chicago","America/Indiana/Knox","America/Indiana/Tell_City","America/Matamoros","America/Menominee","America/North_Dakota/Beulah","America/North_Dakota/Center","America/North_Dakota/New_Salem","America/Rainy_River","America/Rankin_Inlet","America/Resolute","America/Winnipeg","CST6CDT"]},{"value":"Central Standard Time (Mexico)","abbr":"CDT","offset":-5,"isdst":true,"text":"(UTC-06:00) Guadalajara, Mexico City, Monterrey","utc":["America/Bahia_Banderas","America/Cancun","America/Merida","America/Mexico_City","America/Monterrey"]},{"value":"Canada Central Standard Time","abbr":"CCST","offset":-6,"isdst":false,"text":"(UTC-06:00) Saskatchewan","utc":["America/Regina","America/Swift_Current"]},{"value":"SA Pacific Standard Time","abbr":"SPST","offset":-5,"isdst":false,"text":"(UTC-05:00) Bogota, Lima, Quito","utc":["America/Bogota","America/Cayman","America/Coral_Harbour","America/Eirunepe","America/Guayaquil","America/Jamaica","America/Lima","America/Panama","America/Rio_Branco","Etc/GMT+5"]},{"value":"Eastern Standard Time","abbr":"EDT","offset":-4,"isdst":true,"text":"(UTC-05:00) Eastern Time (US & Canada)","utc":["America/Detroit","America/Havana","America/Indiana/Petersburg","America/Indiana/Vincennes","America/Indiana/Winamac","America/Iqaluit","America/Kentucky/Monticello","America/Louisville","America/Montreal","America/Nassau","America/New_York","America/Nipigon","America/Pangnirtung","America/Port-au-Prince","America/Thunder_Bay","America/Toronto","EST5EDT"]},{"value":"US Eastern Standard Time","abbr":"UEDT","offset":-4,"isdst":true,"text":"(UTC-05:00) Indiana (East)","utc":["America/Indiana/Marengo","America/Indiana/Vevay","America/Indianapolis"]},{"value":"Venezuela Standard Time","abbr":"VST","offset":-4.5,"isdst":false,"text":"(UTC-04:30) Caracas","utc":["America/Caracas"]},{"value":"Paraguay Standard Time","abbr":"PST","offset":-4,"isdst":false,"text":"(UTC-04:00) Asuncion","utc":["America/Asuncion"]},{"value":"Atlantic Standard Time","abbr":"ADT","offset":-3,"isdst":true,"text":"(UTC-04:00) Atlantic Time (Canada)","utc":["America/Glace_Bay","America/Goose_Bay","America/Halifax","America/Moncton","America/Thule","Atlantic/Bermuda"]},{"value":"Central Brazilian Standard Time","abbr":"CBST","offset":-4,"isdst":false,"text":"(UTC-04:00) Cuiaba","utc":["America/Campo_Grande","America/Cuiaba"]},{"value":"SA Western Standard Time","abbr":"SWST","offset":-4,"isdst":false,"text":"(UTC-04:00) Georgetown, La Paz, Manaus, San Juan","utc":["America/Anguilla","America/Antigua","America/Aruba","America/Barbados","America/Blanc-Sablon","America/Boa_Vista","America/Curacao","America/Dominica","America/Grand_Turk","America/Grenada","America/Guadeloupe","America/Guyana","America/Kralendijk","America/La_Paz","America/Lower_Princes","America/Manaus","America/Marigot","America/Martinique","America/Montserrat","America/Port_of_Spain","America/Porto_Velho","America/Puerto_Rico","America/Santo_Domingo","America/St_Barthelemy","America/St_Kitts","America/St_Lucia","America/St_Thomas","America/St_Vincent","America/Tortola","Etc/GMT+4"]},{"value":"Pacific SA Standard Time","abbr":"PSST","offset":-4,"isdst":false,"text":"(UTC-04:00) Santiago","utc":["America/Santiago","Antarctica/Palmer"]},{"value":"Newfoundland Standard Time","abbr":"NDT","offset":-2.5,"isdst":true,"text":"(UTC-03:30) Newfoundland","utc":["America/St_Johns"]},{"value":"E. South America Standard Time","abbr":"ESAST","offset":-3,"isdst":false,"text":"(UTC-03:00) Brasilia","utc":["America/Sao_Paulo"]},{"value":"Argentina Standard Time","abbr":"AST","offset":-3,"isdst":false,"text":"(UTC-03:00) Buenos Aires","utc":["America/Argentina/La_Rioja","America/Argentina/Rio_Gallegos","America/Argentina/Salta","America/Argentina/San_Juan","America/Argentina/San_Luis","America/Argentina/Tucuman","America/Argentina/Ushuaia","America/Buenos_Aires","America/Catamarca","America/Cordoba","America/Jujuy","America/Mendoza"]},{"value":"SA Eastern Standard Time","abbr":"SEST","offset":-3,"isdst":false,"text":"(UTC-03:00) Cayenne, Fortaleza","utc":["America/Araguaina","America/Belem","America/Cayenne","America/Fortaleza","America/Maceio","America/Paramaribo","America/Recife","America/Santarem","Antarctica/Rothera","Atlantic/Stanley","Etc/GMT+3"]},{"value":"Greenland Standard Time","abbr":"GDT","offset":-2,"isdst":true,"text":"(UTC-03:00) Greenland","utc":["America/Godthab"]},{"value":"Montevideo Standard Time","abbr":"MST","offset":-3,"isdst":false,"text":"(UTC-03:00) Montevideo","utc":["America/Montevideo"]},{"value":"Bahia Standard Time","abbr":"BST","offset":-3,"isdst":false,"text":"(UTC-03:00) Salvador","utc":["America/Bahia"]},{"value":"UTC-02","abbr":"U","offset":-2,"isdst":false,"text":"(UTC-02:00) Coordinated Universal Time-02","utc":["America/Noronha","Atlantic/South_Georgia","Etc/GMT+2"]},{"value":"Mid-Atlantic Standard Time","abbr":"MDT","offset":-1,"isdst":true,"text":"(UTC-02:00) Mid-Atlantic - Old"},{"value":"Azores Standard Time","abbr":"ADT","offset":0,"isdst":true,"text":"(UTC-01:00) Azores","utc":["America/Scoresbysund","Atlantic/Azores"]},{"value":"Cape Verde Standard Time","abbr":"CVST","offset":-1,"isdst":false,"text":"(UTC-01:00) Cape Verde Is.","utc":["Atlantic/Cape_Verde","Etc/GMT+1"]},{"value":"Morocco Standard Time","abbr":"MDT","offset":1,"isdst":true,"text":"(UTC) Casablanca","utc":["Africa/Casablanca","Africa/El_Aaiun"]},{"value":"UTC","abbr":"CUT","offset":0,"isdst":false,"text":"(UTC) Coordinated Universal Time","utc":["America/Danmarkshavn","Etc/GMT"]},{"value":"GMT Standard Time","abbr":"GDT","offset":1,"isdst":true,"text":"(UTC) Dublin, Edinburgh, Lisbon, London","utc":["Atlantic/Canary","Atlantic/Faeroe","Atlantic/Madeira","Europe/Dublin","Europe/Guernsey","Europe/Isle_of_Man","Europe/Jersey","Europe/Lisbon","Europe/London"]},{"value":"Greenwich Standard Time","abbr":"GST","offset":0,"isdst":false,"text":"(UTC) Monrovia, Reykjavik","utc":["Africa/Abidjan","Africa/Accra","Africa/Bamako","Africa/Banjul","Africa/Bissau","Africa/Conakry","Africa/Dakar","Africa/Freetown","Africa/Lome","Africa/Monrovia","Africa/Nouakchott","Africa/Ouagadougou","Africa/Sao_Tome","Atlantic/Reykjavik","Atlantic/St_Helena"]},{"value":"W. Europe Standard Time","abbr":"WEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna","utc":["Arctic/Longyearbyen","Europe/Amsterdam","Europe/Andorra","Europe/Berlin","Europe/Busingen","Europe/Gibraltar","Europe/Luxembourg","Europe/Malta","Europe/Monaco","Europe/Oslo","Europe/Rome","Europe/San_Marino","Europe/Stockholm","Europe/Vaduz","Europe/Vatican","Europe/Vienna","Europe/Zurich"]},{"value":"Central Europe Standard Time","abbr":"CEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague","utc":["Europe/Belgrade","Europe/Bratislava","Europe/Budapest","Europe/Ljubljana","Europe/Podgorica","Europe/Prague","Europe/Tirane"]},{"value":"Romance Standard Time","abbr":"RDT","offset":2,"isdst":true,"text":"(UTC+01:00) Brussels, Copenhagen, Madrid, Paris","utc":["Africa/Ceuta","Europe/Brussels","Europe/Copenhagen","Europe/Madrid","Europe/Paris"]},{"value":"Central European Standard Time","abbr":"CEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Sarajevo, Skopje, Warsaw, Zagreb","utc":["Europe/Sarajevo","Europe/Skopje","Europe/Warsaw","Europe/Zagreb"]},{"value":"W. Central Africa Standard Time","abbr":"WCAST","offset":1,"isdst":false,"text":"(UTC+01:00) West Central Africa","utc":["Africa/Algiers","Africa/Bangui","Africa/Brazzaville","Africa/Douala","Africa/Kinshasa","Africa/Lagos","Africa/Libreville","Africa/Luanda","Africa/Malabo","Africa/Ndjamena","Africa/Niamey","Africa/Porto-Novo","Africa/Tunis","Etc/GMT-1"]},{"value":"Namibia Standard Time","abbr":"NST","offset":1,"isdst":false,"text":"(UTC+01:00) Windhoek","utc":["Africa/Windhoek"]},{"value":"GTB Standard Time","abbr":"GDT","offset":3,"isdst":true,"text":"(UTC+02:00) Athens, Bucharest","utc":["Asia/Nicosia","Europe/Athens","Europe/Bucharest","Europe/Chisinau"]},{"value":"Middle East Standard Time","abbr":"MEDT","offset":3,"isdst":true,"text":"(UTC+02:00) Beirut","utc":["Asia/Beirut"]},{"value":"Egypt Standard Time","abbr":"EST","offset":2,"isdst":false,"text":"(UTC+02:00) Cairo","utc":["Africa/Cairo"]},{"value":"Syria Standard Time","abbr":"SDT","offset":3,"isdst":true,"text":"(UTC+02:00) Damascus","utc":["Asia/Damascus"]},{"value":"E. Europe Standard Time","abbr":"EEDT","offset":3,"isdst":true,"text":"(UTC+02:00) E. Europe"},{"value":"South Africa Standard Time","abbr":"SAST","offset":2,"isdst":false,"text":"(UTC+02:00) Harare, Pretoria","utc":["Africa/Blantyre","Africa/Bujumbura","Africa/Gaborone","Africa/Harare","Africa/Johannesburg","Africa/Kigali","Africa/Lubumbashi","Africa/Lusaka","Africa/Maputo","Africa/Maseru","Africa/Mbabane","Etc/GMT-2"]},{"value":"FLE Standard Time","abbr":"FDT","offset":3,"isdst":true,"text":"(UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius","utc":["Europe/Helsinki","Europe/Kiev","Europe/Mariehamn","Europe/Riga","Europe/Sofia","Europe/Tallinn","Europe/Uzhgorod","Europe/Vilnius","Europe/Zaporozhye"]},{"value":"Turkey Standard Time","abbr":"TDT","offset":3,"isdst":false,"text":"(UTC+03:00) Istanbul","utc":["Europe/Istanbul"]},{"value":"Israel Standard Time","abbr":"JDT","offset":3,"isdst":true,"text":"(UTC+02:00) Jerusalem","utc":["Asia/Jerusalem"]},{"value":"Libya Standard Time","abbr":"LST","offset":2,"isdst":false,"text":"(UTC+02:00) Tripoli","utc":["Africa/Tripoli"]},{"value":"Jordan Standard Time","abbr":"JST","offset":3,"isdst":false,"text":"(UTC+03:00) Amman","utc":["Asia/Amman"]},{"value":"Arabic Standard Time","abbr":"AST","offset":3,"isdst":false,"text":"(UTC+03:00) Baghdad","utc":["Asia/Baghdad"]},{"value":"Kaliningrad Standard Time","abbr":"KST","offset":3,"isdst":false,"text":"(UTC+03:00) Kaliningrad, Minsk","utc":["Europe/Kaliningrad","Europe/Minsk"]},{"value":"Arab Standard Time","abbr":"AST","offset":3,"isdst":false,"text":"(UTC+03:00) Kuwait, Riyadh","utc":["Asia/Aden","Asia/Bahrain","Asia/Kuwait","Asia/Qatar","Asia/Riyadh"]},{"value":"E. Africa Standard Time","abbr":"EAST","offset":3,"isdst":false,"text":"(UTC+03:00) Nairobi","utc":["Africa/Addis_Ababa","Africa/Asmera","Africa/Dar_es_Salaam","Africa/Djibouti","Africa/Juba","Africa/Kampala","Africa/Khartoum","Africa/Mogadishu","Africa/Nairobi","Antarctica/Syowa","Etc/GMT-3","Indian/Antananarivo","Indian/Comoro","Indian/Mayotte"]},{"value":"Iran Standard Time","abbr":"IDT","offset":4.5,"isdst":true,"text":"(UTC+03:30) Tehran","utc":["Asia/Tehran"]},{"value":"Arabian Standard Time","abbr":"AST","offset":4,"isdst":false,"text":"(UTC+04:00) Abu Dhabi, Muscat","utc":["Asia/Dubai","Asia/Muscat","Etc/GMT-4"]},{"value":"Azerbaijan Standard Time","abbr":"ADT","offset":5,"isdst":true,"text":"(UTC+04:00) Baku","utc":["Asia/Baku"]},{"value":"Russian Standard Time","abbr":"RST","offset":4,"isdst":false,"text":"(UTC+04:00) Moscow, St. Petersburg, Volgograd","utc":["Europe/Moscow","Europe/Samara","Europe/Simferopol","Europe/Volgograd"]},{"value":"Mauritius Standard Time","abbr":"MST","offset":4,"isdst":false,"text":"(UTC+04:00) Port Louis","utc":["Indian/Mahe","Indian/Mauritius","Indian/Reunion"]},{"value":"Georgian Standard Time","abbr":"GST","offset":4,"isdst":false,"text":"(UTC+04:00) Tbilisi","utc":["Asia/Tbilisi"]},{"value":"Caucasus Standard Time","abbr":"CST","offset":4,"isdst":false,"text":"(UTC+04:00) Yerevan","utc":["Asia/Yerevan"]},{"value":"Afghanistan Standard Time","abbr":"AST","offset":4.5,"isdst":false,"text":"(UTC+04:30) Kabul","utc":["Asia/Kabul"]},{"value":"West Asia Standard Time","abbr":"WAST","offset":5,"isdst":false,"text":"(UTC+05:00) Ashgabat, Tashkent","utc":["Antarctica/Mawson","Asia/Aqtau","Asia/Aqtobe","Asia/Ashgabat","Asia/Dushanbe","Asia/Oral","Asia/Samarkand","Asia/Tashkent","Etc/GMT-5","Indian/Kerguelen","Indian/Maldives"]},{"value":"Pakistan Standard Time","abbr":"PST","offset":5,"isdst":false,"text":"(UTC+05:00) Islamabad, Karachi","utc":["Asia/Karachi"]},{"value":"India Standard Time","abbr":"IST","offset":5.5,"isdst":false,"text":"(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi","utc":["Asia/Kolkata"]},{"value":"Sri Lanka Standard Time","abbr":"SLST","offset":5.5,"isdst":false,"text":"(UTC+05:30) Sri Jayawardenepura","utc":["Asia/Colombo"]},{"value":"Nepal Standard Time","abbr":"NST","offset":5.75,"isdst":false,"text":"(UTC+05:45) Kathmandu","utc":["Asia/Katmandu"]},{"value":"Central Asia Standard Time","abbr":"CAST","offset":6,"isdst":false,"text":"(UTC+06:00) Astana","utc":["Antarctica/Vostok","Asia/Almaty","Asia/Bishkek","Asia/Qyzylorda","Asia/Urumqi","Etc/GMT-6","Indian/Chagos"]},{"value":"Bangladesh Standard Time","abbr":"BST","offset":6,"isdst":false,"text":"(UTC+06:00) Dhaka","utc":["Asia/Dhaka","Asia/Thimphu"]},{"value":"Ekaterinburg Standard Time","abbr":"EST","offset":6,"isdst":false,"text":"(UTC+06:00) Ekaterinburg","utc":["Asia/Yekaterinburg"]},{"value":"Myanmar Standard Time","abbr":"MST","offset":6.5,"isdst":false,"text":"(UTC+06:30) Yangon (Rangoon)","utc":["Asia/Rangoon","Indian/Cocos"]},{"value":"SE Asia Standard Time","abbr":"SAST","offset":7,"isdst":false,"text":"(UTC+07:00) Bangkok, Hanoi, Jakarta","utc":["Antarctica/Davis","Asia/Bangkok","Asia/Hovd","Asia/Jakarta","Asia/Phnom_Penh","Asia/Pontianak","Asia/Saigon","Asia/Vientiane","Etc/GMT-7","Indian/Christmas"]},{"value":"N. Central Asia Standard Time","abbr":"NCAST","offset":7,"isdst":false,"text":"(UTC+07:00) Novosibirsk","utc":["Asia/Novokuznetsk","Asia/Novosibirsk","Asia/Omsk"]},{"value":"China Standard Time","abbr":"CST","offset":8,"isdst":false,"text":"(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi","utc":["Asia/Hong_Kong","Asia/Macau","Asia/Shanghai"]},{"value":"North Asia Standard Time","abbr":"NAST","offset":8,"isdst":false,"text":"(UTC+08:00) Krasnoyarsk","utc":["Asia/Krasnoyarsk"]},{"value":"Singapore Standard Time","abbr":"MPST","offset":8,"isdst":false,"text":"(UTC+08:00) Kuala Lumpur, Singapore","utc":["Asia/Brunei","Asia/Kuala_Lumpur","Asia/Kuching","Asia/Makassar","Asia/Manila","Asia/Singapore","Etc/GMT-8"]},{"value":"W. Australia Standard Time","abbr":"WAST","offset":8,"isdst":false,"text":"(UTC+08:00) Perth","utc":["Antarctica/Casey","Australia/Perth"]},{"value":"Taipei Standard Time","abbr":"TST","offset":8,"isdst":false,"text":"(UTC+08:00) Taipei","utc":["Asia/Taipei"]},{"value":"Ulaanbaatar Standard Time","abbr":"UST","offset":8,"isdst":false,"text":"(UTC+08:00) Ulaanbaatar","utc":["Asia/Choibalsan","Asia/Ulaanbaatar"]},{"value":"North Asia East Standard Time","abbr":"NAEST","offset":9,"isdst":false,"text":"(UTC+09:00) Irkutsk","utc":["Asia/Irkutsk"]},{"value":"Tokyo Standard Time","abbr":"TST","offset":9,"isdst":false,"text":"(UTC+09:00) Osaka, Sapporo, Tokyo","utc":["Asia/Dili","Asia/Jayapura","Asia/Tokyo","Etc/GMT-9","Pacific/Palau"]},{"value":"Korea Standard Time","abbr":"KST","offset":9,"isdst":false,"text":"(UTC+09:00) Seoul","utc":["Asia/Pyongyang","Asia/Seoul"]},{"value":"Cen. Australia Standard Time","abbr":"CAST","offset":9.5,"isdst":false,"text":"(UTC+09:30) Adelaide","utc":["Australia/Adelaide","Australia/Broken_Hill"]},{"value":"AUS Central Standard Time","abbr":"ACST","offset":9.5,"isdst":false,"text":"(UTC+09:30) Darwin","utc":["Australia/Darwin"]},{"value":"E. Australia Standard Time","abbr":"EAST","offset":10,"isdst":false,"text":"(UTC+10:00) Brisbane","utc":["Australia/Brisbane","Australia/Lindeman"]},{"value":"AUS Eastern Standard Time","abbr":"AEST","offset":10,"isdst":false,"text":"(UTC+10:00) Canberra, Melbourne, Sydney","utc":["Australia/Melbourne","Australia/Sydney"]},{"value":"West Pacific Standard Time","abbr":"WPST","offset":10,"isdst":false,"text":"(UTC+10:00) Guam, Port Moresby","utc":["Antarctica/DumontDUrville","Etc/GMT-10","Pacific/Guam","Pacific/Port_Moresby","Pacific/Saipan","Pacific/Truk"]},{"value":"Tasmania Standard Time","abbr":"TST","offset":10,"isdst":false,"text":"(UTC+10:00) Hobart","utc":["Australia/Currie","Australia/Hobart"]},{"value":"Yakutsk Standard Time","abbr":"YST","offset":10,"isdst":false,"text":"(UTC+10:00) Yakutsk","utc":["Asia/Chita","Asia/Khandyga","Asia/Yakutsk"]},{"value":"Central Pacific Standard Time","abbr":"CPST","offset":11,"isdst":false,"text":"(UTC+11:00) Solomon Is., New Caledonia","utc":["Antarctica/Macquarie","Etc/GMT-11","Pacific/Efate","Pacific/Guadalcanal","Pacific/Kosrae","Pacific/Noumea","Pacific/Ponape"]},{"value":"Vladivostok Standard Time","abbr":"VST","offset":11,"isdst":false,"text":"(UTC+11:00) Vladivostok","utc":["Asia/Sakhalin","Asia/Ust-Nera","Asia/Vladivostok"]},{"value":"New Zealand Standard Time","abbr":"NZST","offset":12,"isdst":false,"text":"(UTC+12:00) Auckland, Wellington","utc":["Antarctica/McMurdo","Pacific/Auckland"]},{"value":"UTC+12","abbr":"U","offset":12,"isdst":false,"text":"(UTC+12:00) Coordinated Universal Time+12","utc":["Etc/GMT-12","Pacific/Funafuti","Pacific/Kwajalein","Pacific/Majuro","Pacific/Nauru","Pacific/Tarawa","Pacific/Wake","Pacific/Wallis"]},{"value":"Fiji Standard Time","abbr":"FST","offset":12,"isdst":false,"text":"(UTC+12:00) Fiji","utc":["Pacific/Fiji"]},{"value":"Magadan Standard Time","abbr":"MST","offset":12,"isdst":false,"text":"(UTC+12:00) Magadan","utc":["Asia/Anadyr","Asia/Kamchatka","Asia/Magadan","Asia/Srednekolymsk"]},{"value":"Kamchatka Standard Time","abbr":"KDT","offset":13,"isdst":true,"text":"(UTC+12:00) Petropavlovsk-Kamchatsky - Old"},{"value":"Tonga Standard Time","abbr":"TST","offset":13,"isdst":false,"text":"(UTC+13:00) Nuku\'alofa","utc":["Etc/GMT-13","Pacific/Enderbury","Pacific/Fakaofo","Pacific/Tongatapu"]},{"value":"Samoa Standard Time","abbr":"SST","offset":13,"isdst":false,"text":"(UTC+13:00) Samoa","utc":["Pacific/Apia"]}]'
    _timezones = json.loads(_timezones_json)

    _days_as_int = {
        "Sunday": 0
        , "Monday": 1
        , "Tuesday": 2
        , "Wednesday": 3
        , "Thursday": 4
        , "Friday": 5
        , "Saturday": 6
    }
    _week_as_range = {
        "1st": "1-7"
        , "2nd": "8-14"
        , "3rd": "15-21"
        , "4th": "22-28"
    }

    now = datetime.now()

    # write publishSched entries to crontab
    f = open("/tmp/mist_crontab.txt", "w")

    for r_mist_param in rs_mist_params():
        _pull_freq = int(r_mist_param.scPullFreq)
        _row = "%r %r */%r * * python /opt/mist/assets/pull_assets.py > /dev/null 2>&1\n" % (now.minute, now.hour, (_pull_freq/24))
        f.write(_row)

    for r_publish_sched in rs_publish_sched().order_by(main.PublishSched.destSiteName):
        _offset = None

        # get hour offset using given timezone value
        for _zone in _timezones:
            if (_zone['value'] == r_publish_sched.timezone):
                _offset = round(_zone['offset'], 2) # round() to handle offsets with fractional hour values
                break

        _given_hour = int(r_publish_sched.time.split(":")[0])    # extract user-provided hour value
        _given_minute = int(r_publish_sched.time.split(":")[1])    # extract user-provided minute value

        # 1. capture given time and convert to epoch
        now = datetime.now()
        _given_datetime = datetime.strptime("%r %r %r %r:%r" % (now.month, now.day, now.year, _given_hour, _given_minute), '%m %d %Y %H:%M')

        # 2. calculate diff in secs between current local time and current zulu time
        epoch_zulu = int(calendar.timegm(datetime.utcnow().timetuple()))
        epoch_now = int(calendar.timegm(datetime.now().timetuple()))
        epoch_zulu_diff = epoch_now - epoch_zulu
        zulu_diff = epoch_zulu_diff / 3600

        # 3. return calculated hour and minute
        calculated_time = _given_datetime - timedelta(hours=zulu_diff) + timedelta(hours=_offset)

        _this_dayOfMonth = "*"

        if (r_publish_sched.dayOfMonth is not None):
            _this_dayOfMonth = int(r_publish_sched.dayOfMonth)
        elif (r_publish_sched.weekOfMonth is not None):
            _this_dayOfMonth = _week_as_range.get(r_publish_sched.weekOfMonth)

        _this_daysOfWeeks = "*"
        if (r_publish_sched.daysOfWeeks is not None):
            if (r_publish_sched.daysOfWeeks == "Weekdays"):
                _this_daysOfWeeks = "1-5"
            elif (r_publish_sched.daysOfWeeks == "Weekends"):
                _this_daysOfWeeks = "0,6"
            elif re.match('^[A-Za-z]+day$', r_publish_sched.daysOfWeeks):
                _this_daysOfWeeks = _days_as_int[r_publish_sched.daysOfWeeks]  # single digit 0-6

        _this_user = main.session.query(main.MistUser).filter(main.MistUser.username == r_publish_sched.user).first()
        _row = "%r %r %r * %r python /opt/mist/publishing/publish.py --user %r --site \"%r\" %r %r > /dev/null 2>&1\n" % (
            calculated_time.minute, calculated_time.hour, _this_dayOfMonth, _this_daysOfWeeks, _this_user.id, r_publish_sched.destSite,
        r_publish_sched.publishOptions, r_publish_sched.assetOptions)
        _row = _row.replace("'", "")  # remove single quotes

        f.write(_row)
    f.close

    if (os.path.exists("/tmp/mist_crontab.txt")):
        subprocess.Popen(["crontab -r; crontab /tmp/mist_crontab.txt; rm /tmp/mist_crontab.txt"], shell=True,
                         stdout=subprocess.PIPE)

# TODO: refactor authenticate() into User class if possible
class User(object):
    # def __init__(self, id, username, password):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        # self.username = kwargs['username']
        # self.password = kwargs['password']
        # self.username = username
        # self.password = password

    def get(self):
        try:
            main.session.rollback()
            r_user = rs_users().filter(main.MistUser.id == self.id).first()
            if hasattr(r_user, 'username'):
                user = {
                      'id': r_user.id
                    , 'username': r_user.username
                    , 'permission_id': r_user.permission_id
                    , 'subject_dn': r_user.subjectDN
                    , 'first_name': r_user.firstName
                    , 'last_name': r_user.lastName
                    , 'organization': r_user.organization
                    , 'lockout': r_user.lockout
                    , 'permission': r_user.permissions.name
                }
                return jsonify(user)
            else:
                return {"message": "No such user."}
        except (main.ResourceClosedError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (IOError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (AttributeError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.StatementError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}


def authenticate(username, password):
    main.session.rollback()

    # First try logging in with PKI, if cert was sent
    subject_dn = request.environ.get('SSL_CLIENT_S_DN')
    if subject_dn:
        user = main.session.query(main.MistUser).filter(main.and_(main.MistUser.subjectDN == subject_dn, main.MistUser.lockout != "No")).first()
        if user:
            return user

    # Now try logging in with username password
    if not all([username, password]):
        raise JWTError('Bad Request', 'Invalid credentials')

    user = (main.session.query(main.MistUser)
            .filter(
                  main.MistUser.username == username
            ))
    user_query = user.first()

    if (user_query is not None):
        if (int(request.headers.get('Attempts')) >= this_app.config['NUMBER_OF_LOGIN_ATTEMPTS']):
            upd_form = {
                "lockout": "Yes"
            }
            user.update(upd_form)
            return None

    print ("[223] Got here")
    user = (main.session.query(main.MistUser)
            .filter(
                  main.MistUser.username == username
                , main.MistUser.password == hashlib.sha256(password).hexdigest()
                , main.MistUser.lockout == "No"
                , main.MistUser.permission != "0"
            )
            .first())

    # Will return None if nothing matched the query
    return user


def identity(payload):
    user_id = payload['identity']
    return User(id=user_id).get()



def auth_request_handler():
    """
    Override flask_jwt's default auth_request_handler() to not require username and password. In the case of logging
    in with PKI, no username and password will be passed in
    """
    print('[248] Got here')
    data = request.get_json()
    username = data.get(this_app.config.get('JWT_AUTH_USERNAME_KEY'))
    password = data.get(this_app.config.get('JWT_AUTH_PASSWORD_KEY'))

    success = authenticate(username, password)

    if success:
        access_token = jwt.jwt_encode_callback(identity)
        return jwt.auth_response_callback(access_token, identity)
    else:
        raise JWTError('Bad Request', 'Invalid credentials')


def auth_response_handler(access_token, ident):
    """
    Override flask_jwt's default auth_response_handler() method to return not just the access
    token but also the username. In the case of logging in with PKI, you won't already know the username,
    you'll have to get it from the DB and return it here, to pass back to the client.
    """
    print('[267] Got here')
    return jsonify({'access_token': access_token.decode('utf-8'), 'username': ident.username})


jwt = JWT(this_app, authenticate, identity)

# Override defaults for these two methods
jwt.auth_request_handler(auth_request_handler)
jwt.auth_response_handler(auth_response_handler)
# jwt.request_handler()


# NOTE: only used with flask_jwt.jwt_encode_callback()
class _Identity():
    def __init__(self, id):
        self.id = id

# Create and return new JWT token
# Extracts "id" value from previous token embedded in request header and uses it to build new token
def create_new_token(request):
    # incoming_token provided by $httpProvider.interceptor from the browser request
    incoming_token = request.headers.get('authorization').split()[1]

    # value of this_app.config['SECRET_KEY'] is implicitly provided to flask_jwt.jwt_decode_callback()
    # 'SECRET_KEY' is used to decode and validate token
    decoded_token = jwt.jwt_decode_callback(incoming_token)

    # create _Identity instance for use with flask_jwt.jwt_encode_callback()
    obj_identity = _Identity(decoded_token["identity"])
    return jwt.jwt_encode_callback(obj_identity)


def create_full_tag_dname(_id):
    obj_tag = rs_tags().filter(main.Tags.id == _id).first()
    print ("[157] obj_tag.parentID: %r / %r" % (obj_tag.parentID, obj_tag.depth))
    if (obj_tag is not None):
        create_full_tag_dname(obj_tag.parentID)


def create_user_dict(obj_user):
    # 1. Generate user dict
    user = {
          'id': obj_user.id
        , 'username': obj_user.username
        , 'permission_id_new': obj_user.permission_id
        , 'subject_dn': obj_user.subjectDN
        , 'first_name': obj_user.firstName
        , 'last_name': obj_user.lastName
        , 'organization': obj_user.organization
        , 'lockout': obj_user.lockout
        , 'permission_name': obj_user.permissions.name
        , 'permission': obj_user.permission
        , 'repos': {}
        , 'cnt_repos': 0    # if a user has at least one repo assigned then value > 0
    }

    # 2. Generate collection of repo dicts, selecting only repoID, scID, serverName, and repoName
    # NOTE: single distinct() may still result in multiples of identical rows in large recordsets - JWT 28 Nov 2016
    rs_repos_handle = rs_repos().with_entities(main.Repos.repoID.distinct(), main.Repos.scID, main.Repos.serverName, main.Repos.repoName)

    # 3. Generate collection of requested repos and save it to users dict
    rs_requested_repos_access_handle = rs_request_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_requested_repos_access = rs_requested_repos_access_handle.filter(main.requestUserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_requested_repos_access
    for obj_requested_repo_access in obj_requested_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_requested_repo_access.scID, main.Repos.repoID == obj_requested_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            # Create user['repos'] if needed
            for obj_repo in obj_repos:
                identifier = obj_repo.serverName + "," + obj_repo.repoName + "," + str(obj_requested_repo_access.repoID) + "," + str(obj_requested_repo_access.scID)    # create a unique identifier string
                repo_data = str(obj_user.id) + "," + str(obj_requested_repo_access.scID) + "," + str(obj_requested_repo_access.repoID) + "," + obj_user.username # used to populate UserAccess and requestUserAccess tables
                # NOTE: Bootstrap default CSS checkbox-inline used for "cursor: pointer" to indicate clickable resource

                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_requested_repo_access.repoID
                    , 'scID': obj_requested_repo_access.scID
                    , 'is_assigned': 0
                    , 'identifier': identifier
                    , 'repo_data': repo_data
                    , 'class': 'checkbox-inline text-primary'
                    , 'class_glyph': 'checkbox-inline glyphicon glyphicon-plus-sign text-primary'
                    , 'title': 'Requested repo; click to assign to user.'
                }
                user['repos'][identifier] = repo

    # 4. Generate collection of assigned repos and save it to users dict
    rs_repos_access_handle = rs_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_repos_access = rs_repos_access_handle.filter(main.UserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_repos_access
    for obj_repo_access in obj_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_repo_access.scID, main.Repos.repoID == obj_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            for obj_repo in obj_repos:
                identifier = obj_repo.serverName + "," + obj_repo.repoName + "," + str(obj_repo_access.repoID) + "," + str(obj_repo_access.scID)
                repo_data = str(obj_user.id) + "," + str(obj_repo_access.scID) + "," + str(obj_repo_access.repoID) + "," + obj_user.username # used to populate UserAccess and requestUserAccess tables
                # NOTE: Bootstrap default CSS checkbox-inline used for "cursor: pointer" to indicate clickable resource
                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_repo_access.repoID
                    , 'scID': obj_repo_access.scID
                    , 'is_assigned': 1
                    , 'identifier': identifier
                    , 'repo_data': repo_data
                    , 'class': 'checkbox-inline'
                    , 'class_glyph': 'checkbox-inline glyphicon glyphicon-ok-sign text-success'
                    , 'title': 'Assigned repo; click to unassign.'
                    , 'tags': []
                }
                # Add repo if key doesn't yet exist in users['repos'] dict
                if ("identifier" not in user['repos']):
                    user['repos'][identifier] = repo

                obj_tagged_repos = rs_tagged_repos().filter(
                    main.and_(
                          main.TaggedRepos.scID == obj_repo_access.scID
                        , main.TaggedRepos.repoID == obj_repo_access.repoID
                        , main.TaggedRepos.status == "True"
                    )
                )

                if int(obj_tagged_repos.count()) != 0:
                    for obj_tagged_repo in obj_tagged_repos:
                        obj_tags = rs_tags().filter(
                              main.and_(
                                  main.Tags.nameID == obj_tagged_repo.tagID
                                , main.Tags.rollup == obj_tagged_repo.rollup
                              )
                        ).order_by(main.Tags.dname)

                        # TODO: add dname values from parents to list
                        # affiliate IDs for tags belonging to assigned repos
                        if int(obj_tags.count()) != 0:
                            for obj_tag in obj_tags:
                                tag = {
                                      'dname': obj_tag.dname
                                    , 'id': obj_tag.id
                                    , 'rollup': obj_tag.rollup
                                    , 'category': obj_tag.category
                                    , 'tagged_repos_id': obj_tagged_repo.id
                                }
                                user['repos'][identifier]['tags'].append(tag)

                                # create_full_tag_dname(obj_tag.id)

            user['cnt_repos'] += 1    # if a user has at least one repo assigned then value > 0
    return user

def create_repo_dict(obj_repo):
    repo = {
          'repo_id': obj_repo.repoID
        , 'sc_id': obj_repo.scID
        , 'repo_name': obj_repo.repoName
        , 'server_name': obj_repo.serverName
    }
    return repo


# Base class for handling MIST users
class Users(Resource):
    @jwt_required()
    # If get() gets a valid _user value (user ID or username), then the method will return a single user entry
    # If get() is not given a _user value, then the method will return a list of users
    def get(self, _user=None):
        try:
            rs_dict = {}    # used to hold and eventually return users_list[] recordset and associated metadata
            _new_token = create_new_token(request)
            rs_dict['Authorization'] = _new_token   # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

            # query for user/users
            rs_users_handle = rs_users()
            r_single_user = None
            if _user is not None:
                if re.match('^[0-9]+$', _user):
                    r_single_user = rs_users_handle.filter(main.MistUser.id == int(_user)).first()  # use int value for .id
                else:
                    r_single_user = rs_users_handle.filter(main.MistUser.username == _user).first() # use str value for .username

            # add results to users_list[]
            users_list = []
            if _user is None:
                for r_user in rs_users():
                    user_as_dict = create_user_dict(r_user)
                    users_list.append(user_as_dict)
            else:
                users_list.append(create_user_dict(r_single_user))
            rs_dict['users_list'] = users_list  # add users_list[] to rs_dict

            return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

        except (main.NoResultFound) as e:
            print ("[NoResultFound] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': str(e), 'class': 'alert alert-warning'}}
        except (main.StatementError) as e:
            print ("[StatementError] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.OperationalError) as e:
            print ("[OperationalError] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.InvalidRequestError) as e:
            print ("[InvalidRequestError] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.ResourceClosedError) as e:
            print ("[ResourceClosedError] GET /api/v2/user %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.NoSuchColumnError) as e:
            print ("[NoSuchColumnError] GET /api/v2/repos / %s" % str(e))
            return {'response': {'method': 'GET', 'result': 'NoSuchColumnError', 'message': str(e), 'class': 'alert alert-danger'}}

    @jwt_required()
    # 1. Inserts new user into mistUsers table and returns user id
    # 2. Inserts repo and user association into userAccess table
    # Do I even needs this method?!?! Maybe for reference. - JWT 5 Dec 2016
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            new_user = main.MistUser(
                  username=form_fields['username']
                , password=hashlib.sha256(form_fields['password0']).hexdigest()
                , subjectDN=form_fields['subject_dn']
                , firstName=form_fields['first_name']
                , lastName=form_fields['last_name']
                , organization=form_fields['organization']
                , lockout="No"
                , permission_id=2
            )
            main.session.add(new_user)
            main.session.begin_nested()

            for user_repo in form_fields['repos']:
                new_user_access = main.UserAccess(
                      repoID = user_repo['repo_id']
                    , scID = user_repo['sc_id']
                    , userID = new_user.id
                    , userName = form_fields['username']
                )
                main.session.add(new_user_access)
                main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New user added.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (main.IntegrityError) as e:
            print ("[ERROR] POST /api/v2/users / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-warning'}}

    @jwt_required()
    # for a given user ID:
    # 1. Assign one or more selected repos to a given user
    # 2. Update simple fields directly into mistUsers table
    # 3. Extract user ID, username, delete all userAccess rows with that user ID, and insert new rows with user ID, username, scID, and repoID
    # 4. Update permission in mistUsers table
    def put(self, _user):
        try:
            form_fields = request.get_json(force=True)
            permission = None
            if ("permission" in form_fields):
                permission = int(form_fields.pop("permission"))

            # Note whether or not data was from form submission (eg <form> in admin.view.html vs JSON data params)
            assign_submit = None
            if ("assign_submit" in form_fields):
                assign_submit = form_fields["assign_submit"]
                form_fields.pop('assign_submit')

            # May want to refactor form_fields element names to match table column names - JWT 22 Dec 2016
            if ("first_name" in form_fields):
                form_fields["firstName"] = form_fields.pop("first_name")
            if ("last_name" in form_fields):
                form_fields["lastName"] = form_fields.pop("last_name")
            if ("subject_dn" in form_fields):
                form_fields["subjectDN"] = form_fields.pop("subject_dn")
            if ("subject_dn" in form_fields):
                form_fields["subjectDN"] = form_fields.pop("subject_dn")
            if ("permission_id_new" in form_fields):
                form_fields["permission_id"] = form_fields.pop("permission_id_new")
                del form_fields["permission_name"]
            if ("subject_dn" in form_fields):
                form_fields["subjectDN"] = form_fields.pop("subject_dn")
            if ("repos" in form_fields):
                del form_fields["repos"]
            if ("status" in form_fields):
                del form_fields["status"]
            if ("status_class" in form_fields):
                del form_fields["status_class"]


            # ==================================================
            # Set aside any non-MistUser-specific values
            user_admin_toggle = form_fields.pop('user_admin_toggle') if ("user_admin_toggle" in form_fields) else None

            this_user = main.session.query(main.MistUser).filter(main.MistUser.id == int(_user))

            # Used for toggle switch single repo/user assignment
            single_repo = None
            if ("repo" in form_fields):
                single_repo = {}
                single_repo['userID'], single_repo['scID'], single_repo['repoID'], single_repo['userName'] = form_fields.pop('repo').split(',')

            # Keeps count of how many assigned repos a user has
            cnt_repos = None
            if ("cnt_repos" in form_fields):
                cnt_repos = form_fields.pop('cnt_repos')

            # ==================================================
            # POST MULTIPLE REPOS/USER ASSIGNMENTS

            if (assign_submit is not None): # run if action from form submit
                # NOTE: section below is commented out because when user profile was being updated with multiple repos, previously approved repo assignments were being reset to requested - JWT 11 Jan 2017
                # if (assign_submit >= 2):
                #     # Remove all entries from userAccess table containing matched userID value
                #     userAccessEntry = main.session.query(main.UserAccess) \
                #         .filter(main.UserAccess.userID == form_fields['id'])
                #     userAccessEntry.delete()
                # else:
                #     # Remove all entries from requestUserAccess table containing matched userID value
                #     requestUserAccessEntry = main.session.query(main.requestUserAccess) \
                #         .filter(main.requestUserAccess.userID == form_fields['id'])
                #     requestUserAccessEntry.delete()
                # main.session.begin_nested()

                # Set permission to zero if not an admin
                if (permission < 2):
                    upd_form = {
                        "permission": 0
                    }
                    this_user.update(upd_form)
                    main.session.begin_nested()

                # Add any assigned repos to user (if any)
                if ("assign_repos" in form_fields):
                    for assign_repo in form_fields['assign_repos']:
                        repo_id, sc_id = assign_repo.split(',')
                        new_repo_assignment = None

                        if (assign_submit >= 2):    # if update submitter is an admin then add to UserAccess
                            new_repo_assignment = main.UserAccess(
                                  userID=form_fields['id']
                                , scID=sc_id
                                , repoID=repo_id
                                , userName=form_fields['username']
                            )
                        else:   # if update submitter is an admin then add to requestUserAccess
                            new_repo_assignment = main.requestUserAccess(
                                  userID=form_fields['id']
                                , scID=sc_id
                                , repoID=repo_id
                                , userName=form_fields['username']
                            )
                        main.session.add(new_repo_assignment)
                        main.session.begin_nested()

                    # Set permission to 1 if not an admin
                    if (permission < 2):
                        upd_form = {
                            "permission": 1
                        }
                        this_user.update(upd_form)
                        main.session.begin_nested()

                    form_fields.pop('assign_repos')


                # Mark any non-admin user with one or more assigned repos as having user permissions.
                if (permission < 2):
                    upd_form = {
                        "permission": 1 if (cnt_repos > 0) else 0
                    }
                    this_user.update(upd_form)
                    main.session.begin_nested()



            # ==================================================
            # UPDATE GENERAL USER DATA

            # Pass _user value to get mistUser object and update with values in form_fields
            # pdb.set_trace()
            if ("password" in form_fields):
                # If passwords do not match...
                if (('password1' not in form_fields) or (form_fields['password'] != form_fields['password1'])):
                    raise ValueError("Password error: passwords do not match.")

                # If password does not fulfill complexity criteria...
                pw_complexity = PasswordCheck(form_fields['password'])
                error = pw_complexity.check_password()
                if error:
                    raise ValueError("Password error: " + error)

                form_fields["password"] = hashlib.sha256(form_fields["password"]).hexdigest()
                form_fields.pop("password1")

            if (any(form_fields)):
                this_user.update(form_fields)
                db_fields = {}
            main.session.begin_nested()

            # ==================================================
            # TOGGLE USER ADMIN ASSIGNMENTS
            if (user_admin_toggle is not None):
                upd_form = {}
                if (user_admin_toggle > 0):
                    upd_form = {
                        "permission": 2 if permission == 1 else 1   # regular user perms if user has at least one repos assigned
                    }
                else:
                    upd_form = {
                        "permission": 2 if permission == 0 else 0   # no perms if user has no repos assigned
                    }
                this_user.update(upd_form)
                main.session.begin_nested()

            # ==================================================
            # TOGGLE USER REPO ASSIGNMENTS

            # Extract only simple fields (ie not permission, repos) and copy them into db_fields
            if (single_repo is not None):
                single_repo['userID'] = int(single_repo['userID'])
                single_repo['scID'] = str(single_repo['scID'])
                single_repo['repoID'] = int(single_repo['repoID'])
                single_repo['userName'] = str(single_repo['userName'])
                # repo = {key:str(value) for key, value in repo.iteritems()}  # convert to string values

                # Flush any exceptions currently in session
                # main.session.rollback()

                # All repo assignments are saved in requestUserAccess table
                # Repo assignments are marked as approved if also saved in UserAccess table
                # obj_repos = rs_repos_handle.filter(main.and_(main.Repos.sc
                # ID == obj_repo_access.scID, main.Repos.repoID == obj_repo_access.repoID))
                userAccessEntry = main.session.query(main.UserAccess)\
                    .filter(main.and_(main.UserAccess.userID == single_repo['userID'], main.UserAccess.scID == single_repo['scID'], main.UserAccess.repoID == single_repo['repoID']))

                requestUserAccessEntry = main.session.query(main.requestUserAccess)\
                    .filter(main.and_(main.requestUserAccess.userID == single_repo['userID'], main.requestUserAccess.scID == single_repo['scID'], main.requestUserAccess.repoID == single_repo['repoID']))

                # Toggle repo entry between requested and assigned
                if (userAccessEntry.first() is None):   # If user requested to use that repo, and the repo/user assignment is not in userAccessEntry...
                    new_repo_assignment = main.UserAccess(
                          userID = single_repo['userID']
                        , scID = single_repo['scID']
                        , repoID = single_repo['repoID']
                        , userName = single_repo['userName']
                    )
                    main.session.add(new_repo_assignment)  # maybe remove one day? - JWT 1 Dec 2016

                    # # Ignore permission toggle if user is admin
                    # if (this_user_permission < 2):
                    #     upd_form = {
                    #         "permission": 1 if (cnt_repos is not None and permission != 0) else 0
                    #     }
                    #     print "[397] upd_form: %r" % upd_form
                    #     this_user.update(upd_form)

                    main.session.begin_nested()
                    cnt_repos += 1
                    # userAccessEntry.is_assigned = main.current_timestamp  # currently not needed - JWT 2 Dec 2016
                else:                                # add to requested to set as requested
                    userAccessEntry.delete()  # maybe remove one day? - JWT 1 Dec 2016
                    main.session.begin_nested()
                    cnt_repos -= 1
                    # # Ignore permission toggle if user is admin
                    # if (this_user_permission < 2):
                    #     upd_form = {
                    #         "permission": 1 if (cnt_repos is not None and permission != 0) else 0
                    #     }
                    #     print "[412] upd_form: %r" % upd_form
                    #     this_user.update(upd_form)
                    # userAccessEntry.is_assigned = main.current_timestamp  # currently not needed - JWT 2 Dec 2016

                # Mark any non-admin user with one or more assigned repos as having user permissions.
                if (permission < 2):
                    upd_form = {
                        "permission": 1 if (cnt_repos > 0) else 0
                    }
                    this_user.update(upd_form)
                    main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'User successfully updated.', 'class': 'alert alert-success', 'user_id': int(_user)}}

        except (ValueError) as e:
            print ("[ValueError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'AttributeError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (AttributeError) as e:
            print ("[AttributeError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'AttributeError', 'message': e, 'class': 'alert alert-danger'}}
        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
        except (TypeError) as e:
            print ("[TypeError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'TypeError', 'message': 'TypeError', 'class': 'alert alert-danger'}}
        except (main.NoSuchColumnError) as e:
            print ("[NoSuchColumnError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'NoSuchColumnError', 'message': e, 'class': 'alert alert-danger'}}

    @jwt_required()
    # removes user and their affiliated repos
    def delete(self, _user):
        if re.match('^[0-9]+$', _user):
            # use int value for .id
            main.session.query(main.requestUserAccess).filter(main.requestUserAccess.userID == int(_user)).delete()
            main.session.query(main.UserAccess).filter(main.UserAccess.userID == int(_user)).delete()
            main.session.query(main.MistUser).filter(main.MistUser.id == int(_user)).delete()
        else:
            # use str value for .username
            main.session.query(main.requestUserAccess).filter(main.requestUserAccess.userName == _user).delete()
            main.session.query(main.UserAccess).filter(main.UserAccess.userName == _user).delete()
            main.session.query(main.MistUser).filter(main.MistUser.username == _user).delete()

        main.session.commit()
        if re.match('^[0-9]+$', _user):
            # use int value for .id
            return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'User successfully deleted.', 'class': 'alert alert-success', 'user_id': int(_user)}}
        else:
            # use str value for .username
            return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'User successfully deleted.', 'class': 'alert alert-success', 'user_id': _user}}


class Signup(Resource):
    def get(self):
        return {'message': 'No GET method for this endpoint.'}
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            # If passwords do not match...
            if (form_fields['password0'] != form_fields['password1']):
                raise ValueError("Password error: passwords do not match.")

            # If password does not fulfill complexity criteria...
            pw_complexity = PasswordCheck(form_fields['password0'])
            error = pw_complexity.check_password()
            if error:
                raise ValueError("Password error: " + error)

            new_user = main.MistUser(
                username=form_fields['username'],
                password=hashlib.sha256(form_fields['password0']).hexdigest(),
                subjectDN=request.environ.get('SSL_CLIENT_S_DN', 'No certs'),
                firstName=form_fields['first_name'],
                lastName=form_fields['last_name'],
                organization=form_fields['organization'],
                lockout="Yes",
                permission=0,
                permission_id=1
            )

            main.session.add(new_user)
            main.session.begin_nested()

            for user_repo in form_fields['repos']:
                new_user_access = main.requestUserAccess(
                      repoID = int(user_repo['repo_id'])
                    , scID = user_repo['sc_id']
                    , userID = new_user.id
                    , userName = form_fields['username']
                )
                main.session.add(new_user_access)
                main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'User information submitted. Information will be reviewed and admin will contact you when approved.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'], e))
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-danger'}}

    def put(self, _user=None):
        return {'message': 'No PUT method for this endpoint.'}
    def delete(self, _user=None):
        return {'message': 'No DELETE method for this endpoint.'}


class Repos(Resource):
    # @jwt_required()
    def get(self):
        try:
            # returns list of repos from Repos table
            # (NOTE: since there's no dedicated normalized table for just repos, all combinations of returned fields from Repos are distinct)
            rs_dict = {}    # used to hold and eventually return repos_list[] recordset and associated metadata
            # _new_token = create_new_token(request)
            # rs_dict['Authorization'] = _new_token   # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

            # NOTE: main.Repos.id is not being returned since Repos table is not properly normalized and including id will result in returning duplicates - JWT 7 Nov 2016
            main.session.rollback()
            rs_repos_handle = rs_repos().group_by(main.Repos.repoID, main.Repos.scID, main.Repos.repoName, main.Repos.serverName)\
                .order_by(main.Repos.serverName, main.Repos.repoName)

            # add results to repos_list[]
            repos_list = []
            for r_repo in rs_repos_handle:
                repos_list.append(create_repo_dict(r_repo))
            rs_dict['repos_list'] = repos_list  # add repos_list[] to rs_dict

            return rs_dict  # return rs_dict

        except (AttributeError) as e:
            print ("[AttributeError] GET /api/v2/repos / %s" % e)
            return {'response': {'method': 'GET', 'result': 'AttributeError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.ResourceClosedError) as e:
            print ("[ResourceClosedError] GET /api/v2/repos / %s" % str(e))
            return {'response': {'method': 'GET', 'result': 'ResourceClosedError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] GET /api/v2/repos / %s" % e)
            return {'response': {'method': 'GET', 'result': 'ProgrammingError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.OperationalError) as e:
            print ("[OperationalError] GET /api/v2/repos / %s" % str(e))
            return {'response': {'method': 'GET', 'result': 'OperationalError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (TypeError) as e:
            print ("[TypeError] GET /api/v2/repos / %s" % e)
            return {'response': {'method': 'GET', 'result': 'TypeError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.StatementError) as e:
            print ("[StatementError] GET /api/v2/repos / %s" % str(e))
            return {'response': {'method': 'GET', 'result': 'StatementError', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.NoSuchColumnError) as e:
            print ("[NoSuchColumnError] GET /api/v2/repos / %s" % str(e))
            return {'response': {'method': 'GET', 'result': 'NoSuchColumnError', 'message': str(e), 'class': 'alert alert-danger'}}


    def post(self):
        # TODO: will use for inserting new repo entries
        form_fields = request.get_json(force=True)
        return {'response': {'foo': form_fields}}
    def put(self, _user=None):
        # TODO: will use for updating existing repo entries
        return {'message': 'No PUT method for this endpoint.'}
    def delete(self, _user=None):
        # TODO: will use for deleting repo entries
        return {'message': 'No DELETE method for this endpoint.'}


class SecurityCenter(Resource):
    @jwt_required()
    # If get() gets a valid _user value (user ID or username), then the method will return a single user entry
    # If get() is not given a _user value, then the method will return a list of users
    def get(self, _id=None):
        try:
            rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
            _new_token = create_new_token(request)
            rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

            rs_sc_handle = rs_security_centers().order_by(main.SecurityCenter.serverName)
            r_single_sc = None
            if _id is not None:
                r_single_sc = rs_sc_handle.filter(
                    main.SecurityCenter.id == int(_id)
                ).first()

            # add results to sc_list
            sc_list = []
            if _id is None:
                for r_sc in rs_sc_handle:
                    sc_list.append(row_to_dict(r_sc))
            else:
                sc_list.append(row_to_dict(r_single_sc))

            rs_dict['sc_list'] = sc_list  # add users_list[] to rs_dict

            return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

        except (main.NoResultFound) as e:
            print ("[NoResultFound] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (AttributeError) as e:
            print ("[AttributeError] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (TypeError) as e:
            print ("[TypeError] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}

    @jwt_required()
    def post(self):
        try:
            form_fields = {}
            for key, value in request.form.iteritems():
                if (key != 'id' and key != 'status' and key != 'status_class'):   # don't need "id" since value is being provided by _id, may want to replace with regex in future
                    form_fields[key] = value

            if ('certificateFile' in request.files):
                certificateFile = request.files['certificateFile']
                certificateFile_name = secure_filename(certificateFile.filename)
                if (not os.path.exists(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'])):
                    try:
                        os.makedirs(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'])
                    except OSError as exc:
                        if exc.errno != 17:
                            raise
                certificateFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], certificateFile_name))
                form_fields['certificateFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + certificateFile_name

            if ('keyFile' in request.files):
                keyFile = request.files['keyFile']
                keyFile_name = secure_filename(keyFile.filename)
                if (not os.path.exists(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'])):
                    try:
                        os.makedirs(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'])
                    except OSError as exc:
                        if exc.errno != 17:
                            raise
                keyFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], keyFile_name))
                form_fields['keyFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + keyFile_name

            new_sc = main.SecurityCenter(
                  fqdn_IP = form_fields['fqdn_IP']
                , serverName = form_fields['serverName']
                , version = form_fields['version']
                , username = form_fields['username'] if ("username" in form_fields) else None
                , pw = form_fields['pw'] if ("pw" in form_fields) else None
                , certificateFile = form_fields['certificateFile'] if ("certificateFile" in form_fields) else None
                , keyFile = form_fields['keyFile'] if ("keyFile" in form_fields) else None
            )

            main.session.add(new_sc)
            main.session.commit()
            main.session.flush()

            # pull assets from newly added Security Center appliance
            subprocess.Popen(["python /opt/mist/assets/pull_assets.py"], shell=True, stdout=subprocess.PIPE)

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New SecurityCenter entry submitted.', 'class': 'alert alert-success', 'user_id': int(new_sc.id)}}

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-danger'}}

    @jwt_required()
    def put(self, _id=None):
        try:
            form_fields = {}
            for key, value in request.form.iteritems():
                if (key != 'id' and key != 'status' and key != 'status_class'):   # don't need "id" since value is being provided by _id, may want to replace with regex in future
                    form_fields[key] = value

            if ('certificateFile' in request.files):
                certificateFile = request.files['certificateFile']
                certificateFile_name = secure_filename(certificateFile.filename)
                certificateFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], certificateFile_name))
                form_fields['certificateFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + certificateFile_name

            if ('keyFile' in request.files):
                keyFile = request.files['keyFile']
                keyFile_name = secure_filename(keyFile.filename)
                keyFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], keyFile_name))
                form_fields['keyFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + keyFile_name

            form_fields.pop('$$hashKey')    # remove files node now that we're done with them

            this_sc = main.session.query(main.SecurityCenter).filter(main.SecurityCenter.id == int(_id))

            if ("pw" in form_fields):
                form_fields["pw"] = base64.b64encode(form_fields["pw"]) # need to check if b64 is the right hash algorithm - JWT 12 Dec 2016
            if (any(form_fields)):
                this_sc.update(form_fields)
                main.session.commit()
                main.session.flush()

            # pull assets from newly updated Security Center appliance
            subprocess.Popen(["python /opt/mist/assets/pull_assets.py"], shell=True, stdout=subprocess.PIPE)

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'SecurityCenter successfully updated.', 'class': 'alert alert-success', '_id': int(_id)}}

        except (ValueError) as e:
            print ("[ValueError] PUT /api/v2/securitycenter/%s / %s" % (_id, e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (AttributeError) as e:
            print ("[AttributeError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'AttributeError', 'message': e, 'class': 'alert alert-danger'}}
        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
        except (TypeError) as e:
            print ("[TypeError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'TypeError', 'message': 'TypeError', 'class': 'alert alert-danger'}}
        except (main.NoSuchColumnError) as e:
            print ("[NoSuchColumnError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'NoSuchColumnError', 'message': e, 'class': 'alert alert-danger'}}

    @jwt_required()
    def delete(self, _id):
        r_sc = main.session.query(main.SecurityCenter).filter(main.SecurityCenter.id == _id).first()
        _sc = row_to_dict(r_sc)

        # 1. Add SC information to removedSCs table
        r_removed_sc = main.session.query(main.RemovedSCs).filter(main.RemovedSCs.scName == _sc['serverName'])
        if (int(r_removed_sc.count()) > 0):
            upd_form = {}
            upd_form["removeDate"] = datetime.now()
            r_removed_sc.update(upd_form)
        else:
            new_removed_sc = main.RemovedSCs(
                  scName = _sc['serverName']
                , removeDate = datetime.now()
                , ack = 'No'
            )
            main.session.add(new_removed_sc)
        main.session.commit()
        main.session.flush()

        # 2. query for Repos based on server name
        r_repos = rs_repos().filter(main.Repos.serverName == _sc['fqdn_IP']).all()

        # 3. Loop through each repo...
        for r_repo in r_repos:

            # Use assetID to delete Assets
            rs_assets().filter(main.Assets.assetID == r_repo.assetID).delete()
            main.session.begin_nested()

            # Use assetID to delete taggedAssets
            rs_tagged_assets().filter(main.TaggedAssets.assetID == r_repo.assetID).delete()
            main.session.begin_nested()

            # Use repoID and scId to delete TaggedRepos
            rs_tagged_repos().filter(
                main.and_(
                    main.TaggedRepos.repoID == r_repo.repoID, main.TaggedRepos.scID == r_repo.scID
                )
            )\
            .delete()
            main.session.begin_nested()

            # Use repoID and scId to delete UserAccess
            rs_user_access().filter(
                main.and_(
                    main.UserAccess.repoID == r_repo.repoID, main.UserAccess.scID == r_repo.scID
                )
            )\
            .delete()
            main.session.begin_nested()

            # Use repoID and scId to delete requestedUserAccess
            rs_request_user_access().filter(
                main.and_(
                    main.requestUserAccess.repoID == r_repo.repoID, main.requestUserAccess.scID == r_repo.scID
                )
            )\
            .delete()
            main.session.begin_nested()

        # 4. Delete selected repos
        rs_repos().filter(main.Repos.serverName == _sc['fqdn_IP']).delete()
        main.session.begin_nested()

        # 5. Delete SecurityCenter
        main.session.query(main.SecurityCenter).filter(main.SecurityCenter.id == _id).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'SecurityCenter successfully deleted.', 'class': 'alert alert-success', 'id': _id}}


class BannerText(Resource):
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata

        rs_banner_text_handle = rs_banner_text().first()

        if (rs_banner_text_handle is None):
            rs_dict['banner_text'] = {"banner_text": ""}
        else:
            rs_dict['banner_text'] = rs_banner_text_handle.BannerText  # add users_list[] to rs_dict

        return jsonify(rs_dict) # return rs_dict

    @jwt_required()
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            new_banner_text = main.BannerText(
                  BannerText = form_fields['banner_text']
            )

            main.session.add(new_banner_text)
            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New Banner Text entry submitted.', 'class': 'alert alert-success'}}

        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/bannertext / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}

    def put(self, _user=None):
        # TODO: will use for updating existing repo entries
        return {'response': {'method': 'PUT', 'result': 'success', 'message': 'No PUT method for this endpoint.', 'class': 'alert alert-warning'}}

    @jwt_required()
    def delete(self):
        main.session.query(main.BannerText).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Banner Text successfully deleted.', 'class': 'alert alert-success'}}


class Classification(Resource):
    def get(self, _id=None):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata

        rs_classification_handle = rs_classification().order_by(main.Classifications.index)
        r_single_classification = None
        if _id is not None:
            r_single_classification = rs_classification_handle.filter(
                main.Classifications.selected == "Y"
            ).first()

        # add results to classifications_list
        classifications_list = []
        if _id is None:
            for r_classification in rs_classification_handle:
                classifications_list.append(row_to_dict(r_classification))
        else:
            classifications_list.append(row_to_dict(r_single_classification))

        rs_dict['classifications_list'] = classifications_list  # add users_list[] to rs_dict

        return jsonify(rs_dict)  # return rs_dict

    def post(self):
        return {'response': {'method': 'POST', 'result': 'success', 'message': 'No POST method for this endpoint.', 'class': 'alert alert-warning'}}

    @jwt_required()
    def put(self, _id=None):
        try:
            # update all "selected" values as N
            upd_form = {}
            upd_form["selected"] = "N"

            classification_selected = rs_classification().filter(main.Classifications.selected == 'Y')
            classification_selected.update(upd_form)

            main.session.commit()
            main.session.flush()

            # update "selected" as Y where index = _id
            upd_form["selected"] = "Y"
            classification_selected = rs_classification().filter(main.Classifications.index == _id)
            classification_selected.update(upd_form)
            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Classification successfully updated.', 'class': 'alert alert-success', '_id': int(_id)}}

        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}

    def delete(self):
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'No DELETE method for this endpoint.', 'class': 'alert alert-warning'}}


class MistParams(Resource):
    @jwt_required()
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        # add results to mist_params_list[]
        mist_params_list = []
        for r_mist_param in rs_mist_params():
            mist_params_list.append(row_to_dict(r_mist_param))
        rs_dict['mist_params_list'] = mist_params_list  # add mist_params_list[] to rs_dict

        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    def post(self):
        return {'response': {'method': 'POST', 'result': 'success', 'message': 'No POST method for this endpoint.', 'class': 'alert alert-warning'}}

    @jwt_required()
    def put(self, _field_name, _value):
        try:
            upd_form = {}
            upd_form[_field_name] = _value

            rs_mist_params().update(upd_form)
            main.session.commit()
            main.session.flush()

            if (_field_name == "scPullFreq"):
                # 1. Call initial pull command
                subprocess.Popen(["python /opt/mist/assets/pull_assets.py"], shell=True, stdout=subprocess.PIPE)
                # 2. Update cron job
                write_crontab()

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Parameter successfully updated.', 'class': 'alert alert-success', '_value': int(_value)}}

        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/params/%s/%s / %s" % (_field_name, _value, e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}

    def delete(self):
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'No DELETE method for this endpoint.', 'class': 'alert alert-warning'}}


class TagDefinitions(Resource):
    # @jwt_required()
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        tag_definitions_list = []

        for r_tag_definition in rs_tag_definitions().order_by(main.TagDefinitions.id):
            tag_definitions_list.append(row_to_dict(r_tag_definition))

        # convert certain values from string to integer
        for _index, row in enumerate(tag_definitions_list):
            for key, value in row.iteritems():
                if ((key == "id" or key == "defaultValue") and (value != "") and (value != "None")):
                    tag_definitions_list[_index][key] = int(value)

        rs_dict['tag_definitions'] = tag_definitions_list
        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    @jwt_required()
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            new_td = main.TagDefinitions(
                  name = form_fields['name']
                , title = form_fields['title']
                , description = form_fields['description'] if ("description" in form_fields) else "TBD"
                , required = form_fields['required']
                , defaultValue = form_fields['defaultValue'] if ("defaultValue" in form_fields) else None
                , type = form_fields['type'] if ("type" in form_fields) else "plaintext"
                , cardinality = form_fields['cardinality'] if ("cardinality" in form_fields) else 1
                , version = form_fields['version'] if ("version" in form_fields) else "1.0"
                , rollup = form_fields['rollup']
                , category = form_fields['category']
                , timestamp = datetime.now()
            )

            main.session.add(new_td)
            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New tag definition entry submitted.', 'class': 'alert alert-success', 'id': int(new_td.id)}}

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/tagdefinitions / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/tagdefinitions / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/tagdefinitions / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted tag definition already exists.', 'class': 'alert alert-danger'}}

    @jwt_required()
    def put(self, _id):
        try:
            upd_form = request.get_json(force=True)

            rs_tag_definitions().filter(main.TagDefinitions.id == _id).update(upd_form)

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Tag definition value successfully updated.', 'class': 'alert alert-success', '_id': _id}}

        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/securitycenter/%s / %s" % (_id,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}

    @jwt_required()
    def delete(self, _id):
        main.session.query(main.TagDefinitions).filter(main.TagDefinitions.id == _id).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Tag definition successfully deleted.', 'class': 'alert alert-success', 'id': int(_id)}}


class PublishSites(Resource):
    @jwt_required()
    def get(self):
        _new_token = create_new_token(request)
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        publish_sites_list = []

        for r_publish_site in rs_publish_sites().order_by(main.PublishSites.id):
            publish_sites_list.append(row_to_dict(r_publish_site))

        for site in publish_sites_list:
            site['id'] = int(site['id'])

        rs_dict['publish_sites_list'] = publish_sites_list
        resp = jsonify(rs_dict)
        resp.status_code = 200
        resp.headers['Authorization'] = _new_token
        return resp  # return rs_dict

    @jwt_required()
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            new_entry = main.PublishSites(
                  location=form_fields['location']
                , name=form_fields['name']
            )

            main.session.add(new_entry)
            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New publish site entry submitted.',
                                 'class': 'alert alert-success', 'id': int(new_entry.id)}}

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/publishsites / %s" % e)
            main.session.rollback()
            return {
                'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/publishsites / %s" % e)
            main.session.rollback()
            return {
                'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/publishsites / %s" % e)
            main.session.rollback()
            return {
                'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted publish site already exists.',
                             'class': 'alert alert-danger'}}

    @jwt_required()
    def put(self, _id):
        try:
            upd_form = request.get_json(force=True)

            rs_publish_sites().filter(main.PublishSites.id == _id).update(upd_form)

            main.session.commit()
            main.session.flush()

            return {
                'response': {'method': 'PUT', 'result': 'success', 'message': 'Publish site successfully updated.',
                             'class': 'alert alert-success', '_id': _id}}

        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/publishsite/%s / %s" % (_id, e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e,
                                 'class': 'alert alert-danger'}}

    @jwt_required()
    def delete(self, _id):
        main.session.query(main.PublishSites).filter(main.PublishSites.id == _id).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Publish site item successfully deleted.',
                             'class': 'alert alert-success', 'id': int(_id)}}


class CategorizedTags(Resource):
    @jwt_required()
    def get(self, _td_id):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        _top = {"treeData": {"id": 0, "data": []}}
        raw_tags_list = []

        for r_tag in rs_tags().filter(main.Tags.tag_definition_id == _td_id).order_by(main.Tags.dname):
            _this_tag = row_to_dict(r_tag)
            _this_tag["value"] = _this_tag["dname"]
            raw_tags_list.append(_this_tag)

        tags = dict((elem["nameID"], elem) for elem in raw_tags_list)
        for elem in raw_tags_list:
            if elem["parentID"] != "Top":
                if "data" not in tags[elem["parentID"]]:
                    tags[elem["parentID"]]['data'] = []
                tags[elem["parentID"]]['data'].append(tags[elem["nameID"]])

        for key in tags.iterkeys():
            if tags[key]['parentID'] == "Top":
                _top['treeData']['data'].append(tags[key])

        rs_dict['tags'] = _top

        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    # @jwt_required()
    def post(self):
        return {'response': {'method': 'POST', 'result': 'success', 'message': 'No POST method for this endpoint.', 'class': 'alert alert-warning'}}

    # @jwt_required()
    def put(self, _id):
        return {'response': {'method': 'PUT', 'result': 'success', 'message': 'No PUT method for this endpoint.', 'class': 'alert alert-warning'}}

    # @jwt_required()
    def delete(self, _id):
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'No POST method for this endpoint.', 'class': 'alert alert-warning'}}


class TaggedRepos(Resource):
    # @jwt_required()
    def get(self, _td_id):
        return {'response': {'method': 'GET', 'result': 'success', 'message': 'No GET method for this endpoint.', 'class': 'alert alert-warning'}}

    @jwt_required()
    def post(self):
        try:
            form_fields = request.get_json(force=True)
            username = form_fields['username']
            tree_nodes = form_fields['tree_nodes']
            tagMode = form_fields['tagMode']
            selected_repos = form_fields['selected_repos']
            cardinality = int(form_fields['cardinality'])
            right_now = datetime.now()

            if (len(tree_nodes) <= cardinality):
                for _index_node, _id in enumerate(tree_nodes):  # loop through checked tree nodes
                    for r_tag in rs_tags().filter(main.Tags.id == int(_id)):
                        _this_tag = row_to_dict(r_tag)

                        for _index_repo, _repo in enumerate(selected_repos):  # loop through checked repos
                            # 1. create tagged_repos handle for further use
                            handle_tagged_repos = rs_tagged_repos() \
                                .filter(main.and_
                                (
                                      main.TaggedRepos.status == 'True'
                                    , main.TaggedRepos.repoID == _repo['repo_id']
                                    , main.TaggedRepos.scID == _repo['sc_id']
                                    , main.TaggedRepos.category == _this_tag['category']
                                )
                            )

                            # 2. Insert new tagged repo
                            new_tagged_repo = main.TaggedRepos(
                                repoID=_repo['repo_id']
                                , scID=_repo['sc_id']
                                , tagID=_this_tag['nameID']
                                , rollup=_this_tag['rollup']
                                , category=_this_tag['category']
                                , timestamp=right_now
                                , status="True"
                                , taggedBy=username
                            )
                            main.session.add(new_tagged_repo)
                            main.session.commit()
                            main.session.flush()

                            # 3. Mark extra repos as "false"
                            # select earliest set of IDs to be filtered out
                            # NOTE: .slice() acts as "limit (recordset size) offset cardinality"

                            # Value to be used for SQL limit value
                            num_of_tagged_repos = int(handle_tagged_repos.count())

                            # 5. Mark status of affiliated assets as false for historical purposes
                            upd_form = {
                                "status": 'False'
                            }

                            if (num_of_tagged_repos > cardinality):
                                # Extract IDs of tagged repos to be deleted
                                tagged_repo_ids = []
                                for _tagged_repo in handle_tagged_repos \
                                    .order_by(main.TaggedRepos.timestamp.desc(), main.TaggedRepos.id.desc()) \
                                    .slice(cardinality, num_of_tagged_repos):

                                    tagged_repo_ids.append(int(_tagged_repo.id))

                                    rs_tagged_assets().filter(main.and_
                                            (
                                                  main.TaggedAssets.status == 'True'
                                                , main.TaggedAssets.tagID == _tagged_repo.tagID
                                                , main.TaggedAssets.rollup == _tagged_repo.rollup
                                                , main.TaggedAssets.category == _tagged_repo.category
                                            )
                                        ).update(upd_form)

                                    main.session.commit()
                                    main.session.flush()

                                # Tag all repos with IDs in tagged_repo_ids as false
                                for _id in tagged_repo_ids:
                                    handle_tagged_repos.filter(main.TaggedRepos.id == _id).update(upd_form)

                                # once delete is called transaction must actually be run before anything additional can be done
                                main.session.commit()
                                main.session.flush()

                            for r_repo in rs_repos().filter(
                                main.and_(
                                      main.Repos.repoID == _repo['repo_id']
                                    , main.Repos.scID == _repo['sc_id']
                                )
                            ):
                                _this_repo = row_to_dict(r_repo)

                                new_tagged_asset = main.TaggedAssets(
                                    assetID=_this_repo['assetID']
                                    , tagID=_this_tag['nameID']
                                    , rollup=_this_tag['rollup']
                                    , category=_this_tag['category']
                                    , taggedBy=username
                                    , timestamp=right_now
                                    , status="True"
                                    , tagMode=tagMode
                                )
                                main.session.add(new_tagged_asset)
                                main.session.commit()
                                main.session.flush()


                return {'response': {'method': 'POST', 'result': 'success', 'message': 'New tags applied.', 'class': 'alert alert-success', 'id': 0}}
            else:
                return {'response': {'method': 'POST', 'result': 'error', 'message': 'Number of tags (' + str(len(tree_nodes)) + ') exceeds cardinality (' + str(cardinality) + '). Stopping.', 'class': 'alert alert-danger'}}


        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/taggedrepos / %s" % e)
            main.session.rollback()
            return {
                'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/taggedrepos / %s" % e)
            main.session.rollback()
            return {
                'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
            # except (main.IntegrityError) as e:
            #     print ("[IntegrityError] POST /api/v2/someclass / %s" % e)
            #     main.session.rollback()
            #     return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted something already exists.', 'class': 'alert alert-danger'}}

    # @jwt_required()
    def put(self, _id):
        return {'response': {'method': 'PUT', 'result': 'success', 'message': 'No POST method for this endpoint.',
                             'class': 'alert alert-warning'}}

    @jwt_required()
    def delete(self, _tagged_repo_id):
        obj_tagged_repo = rs_tagged_repos().filter(main.TaggedRepos.id == _tagged_repo_id).first()

        upd_form = {
            "status": 'False'
        }
        rs_tagged_assets().filter(
            main.and_(
                  main.TaggedAssets.tagID == obj_tagged_repo.tagID
                , main.TaggedAssets.rollup == obj_tagged_repo.rollup
                , main.TaggedAssets.category == obj_tagged_repo.category
                , main.TaggedAssets.status == 'True'
            )
        ).update(upd_form)
        main.session.commit()
        main.session.flush()

        rs_tagged_repos().filter(main.TaggedRepos.id == _tagged_repo_id).update(upd_form)
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Tagged repo item successfully deleted.',
                             'class': 'alert alert-success', 'id': int(_tagged_repo_id)}}


# Generic model class template
class Assets(Resource):
    @jwt_required()
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        tagged_assets_list = []

        handle_tagged_assets = main.session.query(main.TaggedAssets, main.Tags, main.Assets)\
            .join(
                main.Tags, main.and_(
                    main.TaggedAssets.tagID == main.Tags.nameID, main.TaggedAssets.category == main.Tags.category, main.TaggedAssets.rollup == main.Tags.rollup
                )
            )\
            .join(main.Assets, main.TaggedAssets.assetID == main.Assets.assetID)\
            .filter(main.TaggedAssets.status == "true")\
            .order_by(main.TaggedAssets.timestamp.desc())\
            .all()

        for r_tagged_asset in handle_tagged_assets:
            _tagged_asset = row_to_dict(r_tagged_asset.TaggedAssets)
            _tagged_asset['dname'] = r_tagged_asset.Tags.dname
            _tagged_asset['macAddress'] = r_tagged_asset.Assets.macAddress
            _tagged_asset['biosGUID'] = r_tagged_asset.Assets.biosGUID
            _tagged_asset['ip'] = r_tagged_asset.Assets.ip
            _tagged_asset['lastUnauthRun'] = r_tagged_asset.Assets.lastUnauthRun
            _tagged_asset['state'] = r_tagged_asset.Assets.state
            _tagged_asset['osCPE'] = r_tagged_asset.Assets.osCPE
            _tagged_asset['netbiosName'] = r_tagged_asset.Assets.netbiosName
            _tagged_asset['dnsName'] = r_tagged_asset.Assets.dnsName
            _tagged_asset['lastAuthRun'] = r_tagged_asset.Assets.lastAuthRun
            _tagged_asset['published'] = r_tagged_asset.Assets.published
            _tagged_asset['purged'] = r_tagged_asset.Assets.purged
            _tagged_asset['mcafeeGUID'] = r_tagged_asset.Assets.mcafeeGUID
            tagged_assets_list.append(_tagged_asset)

        rs_dict['tagged_assets_list'] = tagged_assets_list
        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    @jwt_required()
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            # NOTE: this really should be in the .get() method but I can't figure out how to pass multiple distinct values through an endpoint
            # and a GET request does not contain data. - JWT 14 Feb 2017
            if ((form_fields['action'] == "search_assets") or ('cardinality' not in form_fields)):
                rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
                _new_token = create_new_token(request)
                rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

                assets_list = []
                asset_filters = {}

                # create assets object handle
                handle_assets = rs_assets()\
                    .order_by(main.Assets.assetID)

                # category select and free type field
                if ('search_value' in form_fields):
                    if (form_fields['category'][:7] == "assets_"):  # If search term is an Assets row value...
                        if (form_fields['category'][7:] == "ip"):
                            ip_list = []
                            if ("/" in form_fields['search_value']):    # query IP by CIDR
                                for item in list(netaddr.IPNetwork(form_fields['search_value']).iter_hosts()):  # iterate through collection of IPAddress objects
                                    ip_list.append(item.format())   # .format() extracts address from IPAddress object
                            elif ("-" in form_fields['search_value']):   # assume query IP by range
                                _first, _last = form_fields['search_value'].split("-")
                                netaddr.iter_iprange(_first, _last)
                                for item in netaddr.iter_iprange(_first, _last):    # iterate through collection of IPAddress objects
                                    ip_list.append(item.format())   # .format() extracts address from IPAddress object
                            else:
                                ip_list.append(form_fields['search_value'])
                            handle_assets = handle_assets\
                                .filter(main.Assets.ip.in_(ip_list))

                            # https://dev.mysql.com/doc/refman/5.7/en/miscellaneous-functions.html#function_inet-aton
                            # NOTE: the code below should be used when
                            # 1. MySQL is updated to v5.6 or higher
                            # 2. an IP column is provided that allows for a
                            # if ("/" in form_fields['search_value']):    # query IP by CIDR
                            #     _first_as_int = netaddr.IPNetwork(form_fields['search_value']).first
                            #     _last_as_int = netaddr.IPNetwork(form_fields['search_value']).last
                            #     # _ip, _cidr = form_fields['search_value'].split("/")
                            # else:   # assume query IP by range
                            #     _first, _last = form_fields['search_value'].split("-")
                            #     _first_as_int = inet_aton(_first)
                            #     _last_as_int = inet_aton(_last)
                            # handle_assets = handle_assets\
                            #     .filter(main.between(inet_aton(getattr(main.Assets, "ip")), _first_as_int, _last_as_int))
                        else:
                            asset_filters[form_fields['category'][7:]] = form_fields['search_value']

                            # Using a dynamic filter by providing a dict
                            # http://stackoverflow.com/a/7605366/6554056
                            handle_assets = handle_assets\
                                .filter(
                                    getattr(main.Assets, form_fields['category'][7:])
                                        .like("%"+form_fields['search_value']+"%")
                                )
                    else:   # If search term is part of a repo name...
                        handle_assets = handle_assets\
                            .join(main.Repos, main.Assets.assetID == main.Repos.assetID)\
                            .filter(
                                main.Repos.repoName.like("%"+form_fields['search_value']+"%")
                            )

                # repo ID dropdown
                if ('repo_id' in form_fields and form_fields["repo_id"] != -1):
                    handle_assets = handle_assets\
                        .join(main.Repos, main.Assets.assetID == main.Repos.assetID)\
                        .filter(
                            main.and_(main.Repos.repoID == form_fields['repo_id'], main.Repos.scID == form_fields['sc_id'])
                        )

                for r_asset in handle_assets:
                    # Add tags to r_asset
                    assets_list.append(row_to_dict(r_asset))

                for _index_asset, _asset in enumerate(assets_list):
                    assets_list[_index_asset]["tags"] = {}
                    for r_tagged_asset in rs_tagged_assets()\
                        .filter(main.and_(main.TaggedAssets.assetID == _asset['assetID'], main.TaggedAssets.status == 'True')):
                        _tagged_asset = row_to_dict(r_tagged_asset)

                        for r_tag in rs_tags()\
                            .filter(
                                main.and_(
                                      main.Tags.nameID == r_tagged_asset.tagID
                                    , main.Tags.category == r_tagged_asset.category
                                    , main.Tags.rollup == r_tagged_asset.rollup
                                )
                            ).all():
                            _tag = row_to_dict(r_tag)
                            assets_list[_index_asset]["tags"][r_tagged_asset.id] = _tag

                rs_dict['assets_list'] = assets_list
                return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

            # Handling regular form POST
            else:
                username = form_fields['username']
                tree_nodes = form_fields['tree_nodes']
                tagMode = form_fields['tagMode']
                selected_assets = form_fields['selected_assets']
                cardinality = int(form_fields['cardinality'])
                right_now = datetime.now()
                _tags = []

                if (len(tree_nodes) <= cardinality):
                    handle_tags = rs_tags().filter(main.Tags.id.in_(tree_nodes)).order_by(main.Tags.dname)

                    for r_tag in handle_tags:
                        _tags.append(row_to_dict(r_tag))

                    for _index_asset, _asset in enumerate(selected_assets):  # loop through checked assets
                        for _tag in _tags:
                            new_tagged_asset = main.TaggedAssets(
                                  assetID = _asset['assetID']
                                , tagID = _tag['nameID']
                                , rollup = _tag['rollup']
                                , category = _tag['category']
                                , taggedBy = username
                                , timestamp = right_now
                                , status = 'True'
                                , tagMode = tagMode
                            )

                            main.session.add(new_tagged_asset)
                            main.session.commit()
                            main.session.flush()

                            handle_tagged_assets = rs_tagged_assets()\
                                .filter(
                                    main.and_(
                                          main.TaggedAssets.assetID == _asset['assetID']
                                        , main.TaggedAssets.rollup == _tag['rollup']
                                        , main.TaggedAssets.category == _tag['category']
                                        , main.TaggedAssets.status == 'True'
                                    )
                                )

                            num_of_tagged_assets = int(handle_tagged_assets.count())

                            upd_form = {
                                "status": "False"
                            }

                            if (num_of_tagged_assets > cardinality):
                                tagged_asset_ids = []
                                for _tagged_assets in handle_tagged_assets\
                                    .order_by(main.TaggedAssets.timestamp.desc(), main.TaggedAssets.id.desc())\
                                    .slice(cardinality, num_of_tagged_assets):

                                    tagged_asset_ids.append(_tagged_assets.id)

                                rs_tagged_assets()\
                                    .filter(main.TaggedAssets.id.in_(tagged_asset_ids))\
                                    .update(upd_form, synchronize_session='fetch')

                                main.session.commit()
                                main.session.flush()

                    return {'response': {'method': 'POST', 'result': 'success', 'message': 'Asset tagging applied.', 'class': 'alert alert-success', 'id': 1}}
                else:
                    return {'response': {'method': 'POST', 'result': 'error', 'message': 'Number of tags (' + str(len(tree_nodes)) + ') exceeds cardinality (' + str(cardinality) + '). Stopping.', 'class': 'alert alert-danger'}}

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/assets / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
#         except (ValueError) as e:
#             print ("[ValueError] POST /api/v2/someclass / %s" % e)
#             main.session.rollback()
#             return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
#         except (main.IntegrityError) as e:
#             print ("[IntegrityError] POST /api/v2/someclass / %s" % e)
#             main.session.rollback()
#             return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted something already exists.', 'class': 'alert alert-danger'}}
#
#     @jwt_required()
#     def put(self, _id):
#         try:
#             upd_form = request.get_json(force=True)
#
#             rs_some_model().filter(main.SomeModel.id == _id).update(upd_form)
#
#             main.session.commit()
#             main.session.flush()
#
#             return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Some value successfully updated.', 'class': 'alert alert-success', '_id': _id}}
#
#         except (main.ProgrammingError) as e:
#             print ("[ProgrammingError] PUT /api/v2/someclass/%s / %s" % (_id,e))
#             main.session.rollback()
#             return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
#
    @jwt_required()
    def delete(self, _id):
        main.session.query(main.TaggedAssets).filter(main.TaggedAssets.id == _id).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Some item successfully deleted.', 'class': 'alert alert-success', 'id': int(_id)}}



# PublishSched model class template
class PublishSched(Resource):
    @jwt_required()
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        publish_sched_list = []

        for r_publish_sched in rs_publish_sched().order_by(main.PublishSched.destSiteName):
            publish_sched_list.append(row_to_dict(r_publish_sched))

        rs_dict['publish_sched_list'] = publish_sched_list
        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    # @jwt_required()
    # def post(self):
    #     try:
    #         form_fields = request.get_json(force=True)
    #
    #         new_entry = main.SomeModel(
    #               name = form_fields['name']
    #             , description = form_fields['description'] if ("description" in form_fields) else "TBD"
    #             , defaultValue = form_fields['defaultValue'] if ("defaultValue" in form_fields) else None
    #             , type = form_fields['type'] if ("type" in form_fields) else "plaintext"
    #             , cardinality = form_fields['cardinality'] if ("cardinality" in form_fields) else 1
    #             , timestamp = datetime.now()
    #         )
    #
    #         main.session.add(new_entry)
    #         main.session.commit()
    #         main.session.flush()
    #
    #         return {'response': {'method': 'POST', 'result': 'success', 'message': 'New something entry submitted.', 'class': 'alert alert-success', 'id': int(new_entry.id)}}
    #
    #     except (TypeError) as e:
    #         print ("[TypeError] POST /api/v2/someclass / %s" % e)
    #         main.session.rollback()
    #         return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
    #     except (ValueError) as e:
    #         print ("[ValueError] POST /api/v2/someclass / %s" % e)
    #         main.session.rollback()
    #         return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
    #     except (main.IntegrityError) as e:
    #         print ("[IntegrityError] POST /api/v2/someclass / %s" % e)
    #         main.session.rollback()
    #         return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted something already exists.', 'class': 'alert alert-danger'}}
    #
    # @jwt_required()
    # def put(self, _id):
    #     try:
    #         upd_form = request.get_json(force=True)
    #
    #         rs_some_model().filter(main.SomeModel.id == _id).update(upd_form)
    #
    #         main.session.commit()
    #         main.session.flush()
    #
    #         return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Some value successfully updated.', 'class': 'alert alert-success', '_id': _id}}
    #
    #     except (main.ProgrammingError) as e:
    #         print ("[ProgrammingError] PUT /api/v2/someclass/%s / %s" % (_id,e))
    #         main.session.rollback()
    #         return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
    #
    # @jwt_required()
    # def delete(self, _id):
    #     main.session.query(main.SomeModel).filter(main.SomeModel.id == _id).delete()
    #     main.session.commit()
    #     main.session.flush()
    #     return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Some item successfully deleted.', 'class': 'alert alert-success', 'id': int(_id)}}


# RepoPublishTimes model class template
class RepoPublishTimes(Resource):
    @jwt_required()
    def get(self, _show_repos=None):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        repo_publish_times = {}

        if (_show_repos is None):
            # return only the very last entry across all repos
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.arfLast).order_by(main.RepoPublishTimes.arfLast.desc()).limit(1).all():
                repo_publish_times['arfLast'] = r_repo_publish_times.arfLast.strftime("%m/%d/%Y %H:%M:%S")
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.cveLast).order_by(main.RepoPublishTimes.cveLast.desc()).limit(1).all():
                repo_publish_times['cveLast'] = r_repo_publish_times.cveLast.strftime("%m/%d/%Y %H:%M:%S")
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.pluginLast).order_by(main.RepoPublishTimes.pluginLast.desc()).limit(1).all():
                if r_repo_publish_times.pluginLast is not None:
                    repo_publish_times['pluginLast'] = r_repo_publish_times.pluginLast.strftime("%m/%d/%Y %H:%M:%S")
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.benchmarkLast).order_by(main.RepoPublishTimes.benchmarkLast.desc()).limit(1).all():
                if r_repo_publish_times.benchmarkLast is not None:
                    repo_publish_times['benchmarkLast'] = r_repo_publish_times.benchmarkLast.strftime("%m/%d/%Y %H:%M:%S")
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.iavmLast).order_by(main.RepoPublishTimes.iavmLast.desc()).limit(1).all():
                if r_repo_publish_times.iavmLast is not None:
                    repo_publish_times['iavmLast'] = r_repo_publish_times.iavmLast.strftime("%m/%d/%Y %H:%M:%S")
            for r_repo_publish_times in rs_repo_publish_times().with_entities(main.RepoPublishTimes.opattrLast).order_by(main.RepoPublishTimes.opattrLast.desc()).limit(1).all():
                if r_repo_publish_times.opattrLast is not None:
                    repo_publish_times['opattrLast'] = r_repo_publish_times.opattrLast.strftime("%m/%d/%Y %H:%M:%S")

            rs_dict['repo_publish_times'] = repo_publish_times
            return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict
        else:
            handle_unique_repos = rs_repos().with_entities(main.Repos.repoID.distinct(), main.Repos.scID, main.Repos.repoName, main.Repos.serverName)
            _repos_published = {}

            for r_repos_published in handle_unique_repos:
                _repoID, _scID, _repoName, _serverName = r_repos_published
                _key = _serverName + " / " + _repoName

                handle_publish_times_per_repo = rs_repo_publish_times().filter(main.RepoPublishTimes.repoID == _repoID)

                if (handle_publish_times_per_repo.count() > 0):
                    _repos_published[_key] = {}
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.arfLast).order_by(main.RepoPublishTimes.arfLast.desc()).limit(1).all():
                        _repos_published[_key]['arfLast'] = r_repo_publish_times.arfLast.strftime("%m/%d/%Y %H:%M:%S")
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.cveLast).order_by(main.RepoPublishTimes.cveLast.desc()).limit(1).all():
                        _repos_published[_key]['cveLast'] = r_repo_publish_times.cveLast.strftime("%m/%d/%Y %H:%M:%S")
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.pluginLast).order_by(main.RepoPublishTimes.pluginLast.desc()).limit(1).all():
                        _repos_published[_key]['pluginLast'] = r_repo_publish_times.pluginLast.strftime("%m/%d/%Y %H:%M:%S")
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.benchmarkLast).order_by(main.RepoPublishTimes.benchmarkLast.desc()).limit(1).all():
                        _repos_published[_key]['benchmarkLast'] = r_repo_publish_times.benchmarkLast.strftime("%m/%d/%Y %H:%M:%S")
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.iavmLast).order_by(main.RepoPublishTimes.iavmLast.desc()).limit(1).all():
                        _repos_published[_key]['iavmLast'] = r_repo_publish_times.iavmLast.strftime("%m/%d/%Y %H:%M:%S")
                    for r_repo_publish_times in handle_publish_times_per_repo.with_entities(main.RepoPublishTimes.opattrLast).order_by(main.RepoPublishTimes.opattrLast.desc()).limit(1).all():
                        _repos_published[_key]['opattrLast'] = r_repo_publish_times.opattrLast.strftime("%m/%d/%Y %H:%M:%S")

            rs_dict['repo_publish_times'] = _repos_published
            return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    # @jwt_required()
    def post(self):
        return {'response': {'method': 'POST', 'result': 'success', 'message': 'No POST method for this endpoint.', 'class': 'alert alert-warning'}}

    # @jwt_required()
    def put(self, _id):
        return {'response': {'method': 'PUT', 'result': 'success', 'message': 'No PUT method for this endpoint.', 'class': 'alert alert-warning'}}

    # @jwt_required()
    def delete(self, _id):
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'No DELETE method for this endpoint.', 'class': 'alert alert-warning'}}


# PublishJobs model class template
class PublishJobs(Resource):
    @jwt_required()
    def get(self):
        rs_dict = {}  # used to hold and eventually return publish_jobs_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        publish_jobs_list = []

        rollver_days = int(rs_mist_params().first().pubsRollOverPeriod)
        _today = datetime.now()
        _then = _today - timedelta(days=rollver_days)

        # limit by date
        handle_publish_jobs = rs_publish_jobs()\
            .filter(main.between(main.PublishJobs.finishTime, _then, _today))\
            .order_by(main.PublishJobs.finishTime.desc())

        for r_publish_jobs in handle_publish_jobs:
            publish_jobs_list.append(row_to_dict(r_publish_jobs))

        rs_dict['publish_jobs_list'] = publish_jobs_list
        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    @jwt_required()
    def post(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016
        try:
            form_fields = request.get_json(force=True)

            if (form_fields['job_type'] == 'on demand'):
                subprocess.Popen(["/usr/bin/python /opt/mist/publishing/publish.py %s" % form_fields["options"]], shell=True, stdout=subprocess.PIPE)

                rs_dict['response'] = {'method': 'POST', 'result': 'success', 'message': 'Executed publish command on demand.', 'class': 'alert alert-success'}
                return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

            else:
                if (form_fields['id'] != -1):
                    rs_publish_sched().filter(main.PublishSched.id == form_fields['id']).delete()
                    main.session.commit()
                    main.session.flush()

                new_scheduled_job = None
                if (form_fields['freqOption'] == "Monthly(Date)"):
                    new_scheduled_job = main.PublishSched(
                          user = form_fields['user']
                        , destSite = form_fields['destSite']
                        , publishOptions = form_fields['publishOptions']
                        , status = "Scheduled"
                        , assetOptions = form_fields['assetOptions']
                        , destSiteName = form_fields['destSiteName']
                        , dateScheduled = datetime.now()
                        , freqOption = form_fields['freqOption']
                        , time = form_fields['time']
                        , timezone = form_fields['timezone']['value']
                        , dayOfMonth = form_fields['dayOfMonth']
                    )
                elif (form_fields['freqOption'] == "Monthly(Day)"):
                    new_scheduled_job = main.PublishSched(
                          user = form_fields['user']
                        , destSite = form_fields['destSite']
                        , publishOptions = form_fields['publishOptions']
                        , status = "Scheduled"
                        , assetOptions = form_fields['assetOptions']
                        , destSiteName = form_fields['destSiteName']
                        , dateScheduled = datetime.now()
                        , freqOption = form_fields['freqOption']
                        , time = form_fields['time']
                        , timezone = form_fields['timezone']['value']
                        , daysOfWeeks = form_fields['daysOfWeeks']
                        , weekOfMonth = form_fields['weekOfMonth']
                    )
                else:   # "Daily" or "Weekly" by default
                    new_scheduled_job = main.PublishSched(
                          user = form_fields['user']
                        , destSite = form_fields['destSite']
                        , publishOptions = form_fields['publishOptions']
                        , status = "Scheduled"
                        , assetOptions = form_fields['assetOptions']
                        , destSiteName = form_fields['destSiteName']
                        , dateScheduled = datetime.now()
                        , freqOption = form_fields['freqOption']
                        , time = form_fields['time']
                        , timezone = form_fields['timezone']['value']
                        , daysOfWeeks = form_fields['daysOfWeeks']
                    )

                main.session.add(new_scheduled_job)
                main.session.commit()
                main.session.flush()

                write_crontab()

                rs_dict['response'] = {'method': 'POST', 'result': 'success', 'message': 'Executed scheduling publish job.', 'class': 'alert alert-success'}
                return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/publishjobs / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/publishjobs / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/publishjobs / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted something already exists.', 'class': 'alert alert-danger'}}

    # @jwt_required()
    # def put(self, _id):
    #     try:
    #         upd_form = request.get_json(force=True)
    #
    #         rs_some_model().filter(main.SomeModel.id == _id).update(upd_form)
    #
    #         main.session.commit()
    #         main.session.flush()
    #
    #         return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Some value successfully updated.', 'class': 'alert alert-success', '_id': _id}}
    #
    #     except (main.ProgrammingError) as e:
    #         print ("[ProgrammingError] PUT /api/v2/someclass/%s / %s" % (_id,e))
    #         main.session.rollback()
    #         return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
    #
    @jwt_required()
    def delete(self, _id):
        main.session.query(main.PublishSched).filter(main.PublishSched.id == _id).delete()
        main.session.commit()
        main.session.flush()
        write_crontab()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Scheduled job successfully deleted.', 'class': 'alert alert-success', 'id': int(_id)}}


class LocalLogs(Resource):
    @jwt_required()
    def get(self, _name=None):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
        _new_token = create_new_token(request)
        rs_dict['Authorization'] = _new_token  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        _parent_dir = "/var/log/MIST/"
        _log_dirs = [
            {"id": "1", "value": "assets", "data": []},
            {"id": "2", "value": "publishing", "data": []},
            {"id": "3", "value": "tagging", "data": []}
        ]
        _id_to_path_map = {}

        # if filename is provided then parse contents of file provided
        # NOTE: string format is dir_filename
        if _name is not None:
            _dir, _filename = _name.split("_", 1)
            _filetype = _filename.split(".", 1)[1]
            _full_filename = _parent_dir + _dir + "/" + _filename
            _contents = open(_full_filename).read()
            if _filetype == "log":
                rs_dict['log_content'] = {"content": _contents}
            else:
                response = make_response(_contents)
                response.headers["Content-Type"] = "application/gzip"
                response.headers["Content-Disposition"] = "attachment; filename=" + _filename
                return response
        else:
            # otherwise list files from each directory from _log_dirs
            _id = 4
            for _index_dir, _item in enumerate(_log_dirs):
                _dir = _item["value"]
                _files = os.listdir(_parent_dir + _dir)
                for _index_file, _file in enumerate(_files):
                    _files[_index_file] = "/" + _dir + "/" + _file
                    _tree_node = {"id": str(_id), "value": _file}
                    _log_dirs[_index_dir]['data'].append(_tree_node)
                    _id_to_path_map[_id] =  _dir + "_" + _file
                    _id += 1

            rs_dict['local_logs_list'] = _log_dirs
            rs_dict['id_to_path_map'] = _id_to_path_map

        return rs_dict, 200, {"Authorization": _new_token}  # return rs_dict

    def post(self):
        return {'message': 'No POST method for this endpoint.'}

    def put(self, _id):
        return {'message': 'No PUT method for this endpoint.'}

    def delete(self, _id):
        return {'message': 'No DELETE method for this endpoint.'}


# # Generic model class template
# class SomeClass(Resource):
#     @jwt_required()
#     def get(self):
#         rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
#         rs_dict['Authorization'] = create_new_token(request)  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016
#
#         some_list = []
#
#         for r_some_model in rs_some_model().order_by(main.SomeModel.id):
#             some_list.append(row_to_dict(r_some_model))
#
#         rs_dict['some_list'] = some_list
#         return jsonify(rs_dict)  # return rs_dict
#
#     @jwt_required()
#     def post(self):
#         try:
#             form_fields = request.get_json(force=True)
#
#             new_entry = main.SomeModel(
#                   name = form_fields['name']
#                 , description = form_fields['description'] if ("description" in form_fields) else "TBD"
#                 , defaultValue = form_fields['defaultValue'] if ("defaultValue" in form_fields) else None
#                 , type = form_fields['type'] if ("type" in form_fields) else "plaintext"
#                 , cardinality = form_fields['cardinality'] if ("cardinality" in form_fields) else 1
#                 , timestamp = datetime.now()
#             )
#
#             main.session.add(new_entry)
#             main.session.commit()
#             main.session.flush()
#
#             return {'response': {'method': 'POST', 'result': 'success', 'message': 'New something entry submitted.', 'class': 'alert alert-success', 'id': int(new_entry.id)}}
#
#         except (TypeError) as e:
#             print ("[TypeError] POST /api/v2/someclass / %s" % e)
#             main.session.rollback()
#             return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
#         except (ValueError) as e:
#             print ("[ValueError] POST /api/v2/someclass / %s" % e)
#             main.session.rollback()
#             return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
#         except (main.IntegrityError) as e:
#             print ("[IntegrityError] POST /api/v2/someclass / %s" % e)
#             main.session.rollback()
#             return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted something already exists.', 'class': 'alert alert-danger'}}
#
#     @jwt_required()
#     def put(self, _id):
#         try:
#             upd_form = request.get_json(force=True)
#
#             rs_some_model().filter(main.SomeModel.id == _id).update(upd_form)
#
#             main.session.commit()
#             main.session.flush()
#
#             return {'response': {'method': 'PUT', 'result': 'success', 'message': 'Some value successfully updated.', 'class': 'alert alert-success', '_id': _id}}
#
#         except (main.ProgrammingError) as e:
#             print ("[ProgrammingError] PUT /api/v2/someclass/%s / %s" % (_id,e))
#             main.session.rollback()
#             return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
#
#     @jwt_required()
#     def delete(self, _id):
#         main.session.query(main.SomeModel).filter(main.SomeModel.id == _id).delete()
#         main.session.commit()
#         main.session.flush()
#         return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'Some item successfully deleted.', 'class': 'alert alert-success', 'id': int(_id)}}


# PublicationDownloader class
class PublicationDownloader(Resource):
    # @jwt_required()   # users will access this resource directly, not through Angular - request will not contain token
    def get(self, _name=None):
        if (_name is not None):
            _dir, _filename = _name.split("_", 1)
            _fullpath = "/opt/mist/publishing/published_files/%s/%s" % (_dir, _filename)
            response = make_response(open(_fullpath).read())
            response.headers["Content-Type"] = "application/zip"
            response.headers["Content-Disposition"] = "attachment; filename=" + _filename
            return response
        else:
            return "No such file."

# SubjectDN class
class SubjectDN(Resource):
    # @jwt_required()   # users will access this resource directly, not through Angular - request will not contain token
    def get(self):
        rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata

        subject_dn = ""
        if (request.environ.get('SSL_CLIENT_S_DN') is not None):
            subject_dn = request.environ.get('SSL_CLIENT_S_DN')
            rs_dict['subject_dn'] = subject_dn

        return jsonify(rs_dict)  # return rs_dict


# PublicationDownloader class
class ArchivedLogDownloader(Resource):
    # @jwt_required()   # users will access this resource directly, not through Angular - request will not contain token
    def get(self, _name=None):
        if (_name is not None):
            _dir, _filename = _name.split("_", 1)
            _fullpath = "/opt/mist/publishing/published_files/%s/%s" % (_dir, _filename)
            response = make_response(open(_fullpath).read())
            response.headers["Content-Type"] = "application/zip"
            response.headers["Content-Disposition"] = "attachment; filename=" + _filename
            return response
        else:
            return "No such file."

api.add_resource(Users, '/users', '/user/<string:_user>')
api.add_resource(Signup, '/user/signup')
api.add_resource(Repos, '/repos')
api.add_resource(SecurityCenter, '/securitycenters', '/securitycenter/<int:_id>')
api.add_resource(BannerText, '/bannertext')
api.add_resource(Classification, '/classifications', '/classification/<string:_id>')
api.add_resource(MistParams, '/params', '/param/<string:_field_name>/<int:_value>')
api.add_resource(TagDefinitions, '/tagdefinitions', '/tagdefinition/<int:_id>')
api.add_resource(PublishSites, '/publishsites', '/publishsite/<int:_id>')
api.add_resource(CategorizedTags, '/categorizedtags', '/categorizedtags/<int:_td_id>')
api.add_resource(TaggedRepos, '/taggedrepos', '/taggedrepos/<int:_tagged_repo_id>')
api.add_resource(Assets, '/assets', '/assets/<int:_id>')
api.add_resource(PublishSched, '/publishsched')
api.add_resource(PublishJobs, '/publishjobs', '/publishjob/<int:_id>')
api.add_resource(RepoPublishTimes, '/repopublishtimes', '/repopublishtimes/<int:_show_repos>')
api.add_resource(LocalLogs, '/locallogs', '/locallog/<string:_name>')
api.add_resource(PublicationDownloader, '/publicationdownloader/<string:_name>')
api.add_resource(SubjectDN, '/subjectdn')
api.add_resource(ArchivedLogDownloader, '/archivedlogloader/<string:_name>')
