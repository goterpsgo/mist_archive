(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Publish.IndexController', Controller);

    function Controller($state, $scope, $timeout, $localStorage, PublishSchedService, PublishJobsService, RepoPublishTimesService, PublishSitesService, MistParamsService) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['publish.list'] = 'List Available Publications';
        obj_tasks['publish.on_demand'] = 'Publish On Demand or By Schedule';
        obj_tasks['publish.last_dates'] = 'Publish Options Last Dates';
        $scope.publish_sched_list = {};
        $scope.repo_publish_times = {};
        $scope.repo_publish_times_by_repo = {};
        $scope.publish_jobs_list = {};
        vm.publish_sites_list = {};
        $scope.status = '';
        $scope.this_date = new Date();

        $scope.scan_options = {"cve": false, "benchmark": false, "iavm": false, "plugin": false, "all_scan": false, "cleartext": false};
        $scope.asset_options = {"assets": false, "opattr": false, "all_asset": false, "all_opattr": false};

        $scope.grid_options = {
            columnDefs: $scope.column_names,
            // enableSorting: true,
            'data': []
        };
        $scope.publish_mode = 'on demand';
        vm.form_fields = {'job_type': 'on demand'};
        vm.freq_option = ['Daily', 'Weekly', 'Monthly(Date)', 'Monthly(Day)'];
        vm.days_of_weeks = ['Every day', 'Weekdays', 'Weekends'];
        vm.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        vm.days_of_month = [];
        vm.weeks_of_month = ['1st', '2nd', '3rd', '4th'];
        vm.times = [
            '00:00', '00:15', '00:30', '00:45',
            '01:00', '01:15', '01:30', '01:45',
            '02:00', '02:15', '02:30', '02:45',
            '03:00', '03:15', '03:30', '03:45',
            '04:00', '04:15', '04:30', '04:45',
            '05:00', '05:15', '05:30', '05:45',
            '06:00', '06:15', '06:30', '06:45',
            '07:00', '07:15', '07:30', '07:45',
            '08:00', '08:15', '08:30', '08:45',
            '09:00', '09:15', '09:30', '09:45',
            '10:00', '10:15', '10:30', '10:45',
            '11:00', '11:15', '11:30', '11:45',
            '12:00', '12:15', '12:30', '12:45',
            '13:00', '13:15', '13:30', '13:45',
            '14:00', '14:15', '14:30', '14:45',
            '15:00', '15:15', '15:30', '15:45',
            '16:00', '16:15', '16:30', '16:45',
            '17:00', '17:15', '17:30', '17:45',
            '18:00', '18:15', '18:30', '18:45',
            '19:00', '19:15', '19:30', '19:45',
            '20:00', '20:15', '20:30', '20:45',
            '21:00', '21:15', '21:30', '21:45',
            '22:00', '22:15', '22:30', '22:45',
            '23:00', '23:15', '23:30', '23:45'
        ];

        vm.timezones = [{"value":"Dateline Standard Time","abbr":"DST","offset":-12,"isdst":false,"text":"(UTC-12:00) International Date Line West","utc":["Etc/GMT+12"]},{"value":"UTC-11","abbr":"U","offset":-11,"isdst":false,"text":"(UTC-11:00) Coordinated Universal Time-11","utc":["Etc/GMT+11","Pacific/Midway","Pacific/Niue","Pacific/Pago_Pago"]},{"value":"Hawaiian Standard Time","abbr":"HST","offset":-10,"isdst":false,"text":"(UTC-10:00) Hawaii","utc":["Etc/GMT+10","Pacific/Honolulu","Pacific/Johnston","Pacific/Rarotonga","Pacific/Tahiti"]},{"value":"Alaskan Standard Time","abbr":"AKDT","offset":-8,"isdst":true,"text":"(UTC-09:00) Alaska","utc":["America/Anchorage","America/Juneau","America/Nome","America/Sitka","America/Yakutat"]},{"value":"Pacific Standard Time (Mexico)","abbr":"PDT","offset":-7,"isdst":true,"text":"(UTC-08:00) Baja California","utc":["America/Santa_Isabel"]},{"value":"Pacific Standard Time","abbr":"PDT","offset":-7,"isdst":true,"text":"(UTC-08:00) Pacific Time (US & Canada)","utc":["America/Dawson","America/Los_Angeles","America/Tijuana","America/Vancouver","America/Whitehorse","PST8PDT"]},{"value":"US Mountain Standard Time","abbr":"UMST","offset":-7,"isdst":false,"text":"(UTC-07:00) Arizona","utc":["America/Creston","America/Dawson_Creek","America/Hermosillo","America/Phoenix","Etc/GMT+7"]},{"value":"Mountain Standard Time (Mexico)","abbr":"MDT","offset":-6,"isdst":true,"text":"(UTC-07:00) Chihuahua, La Paz, Mazatlan","utc":["America/Chihuahua","America/Mazatlan"]},{"value":"Mountain Standard Time","abbr":"MDT","offset":-6,"isdst":true,"text":"(UTC-07:00) Mountain Time (US & Canada)","utc":["America/Boise","America/Cambridge_Bay","America/Denver","America/Edmonton","America/Inuvik","America/Ojinaga","America/Yellowknife","MST7MDT"]},{"value":"Central America Standard Time","abbr":"CAST","offset":-6,"isdst":false,"text":"(UTC-06:00) Central America","utc":["America/Belize","America/Costa_Rica","America/El_Salvador","America/Guatemala","America/Managua","America/Tegucigalpa","Etc/GMT+6","Pacific/Galapagos"]},{"value":"Central Standard Time","abbr":"CDT","offset":-5,"isdst":true,"text":"(UTC-06:00) Central Time (US & Canada)","utc":["America/Chicago","America/Indiana/Knox","America/Indiana/Tell_City","America/Matamoros","America/Menominee","America/North_Dakota/Beulah","America/North_Dakota/Center","America/North_Dakota/New_Salem","America/Rainy_River","America/Rankin_Inlet","America/Resolute","America/Winnipeg","CST6CDT"]},{"value":"Central Standard Time (Mexico)","abbr":"CDT","offset":-5,"isdst":true,"text":"(UTC-06:00) Guadalajara, Mexico City, Monterrey","utc":["America/Bahia_Banderas","America/Cancun","America/Merida","America/Mexico_City","America/Monterrey"]},{"value":"Canada Central Standard Time","abbr":"CCST","offset":-6,"isdst":false,"text":"(UTC-06:00) Saskatchewan","utc":["America/Regina","America/Swift_Current"]},{"value":"SA Pacific Standard Time","abbr":"SPST","offset":-5,"isdst":false,"text":"(UTC-05:00) Bogota, Lima, Quito","utc":["America/Bogota","America/Cayman","America/Coral_Harbour","America/Eirunepe","America/Guayaquil","America/Jamaica","America/Lima","America/Panama","America/Rio_Branco","Etc/GMT+5"]},{"value":"Eastern Standard Time","abbr":"EDT","offset":-4,"isdst":true,"text":"(UTC-05:00) Eastern Time (US & Canada)","utc":["America/Detroit","America/Havana","America/Indiana/Petersburg","America/Indiana/Vincennes","America/Indiana/Winamac","America/Iqaluit","America/Kentucky/Monticello","America/Louisville","America/Montreal","America/Nassau","America/New_York","America/Nipigon","America/Pangnirtung","America/Port-au-Prince","America/Thunder_Bay","America/Toronto","EST5EDT"]},{"value":"US Eastern Standard Time","abbr":"UEDT","offset":-4,"isdst":true,"text":"(UTC-05:00) Indiana (East)","utc":["America/Indiana/Marengo","America/Indiana/Vevay","America/Indianapolis"]},{"value":"Venezuela Standard Time","abbr":"VST","offset":-4.5,"isdst":false,"text":"(UTC-04:30) Caracas","utc":["America/Caracas"]},{"value":"Paraguay Standard Time","abbr":"PST","offset":-4,"isdst":false,"text":"(UTC-04:00) Asuncion","utc":["America/Asuncion"]},{"value":"Atlantic Standard Time","abbr":"ADT","offset":-3,"isdst":true,"text":"(UTC-04:00) Atlantic Time (Canada)","utc":["America/Glace_Bay","America/Goose_Bay","America/Halifax","America/Moncton","America/Thule","Atlantic/Bermuda"]},{"value":"Central Brazilian Standard Time","abbr":"CBST","offset":-4,"isdst":false,"text":"(UTC-04:00) Cuiaba","utc":["America/Campo_Grande","America/Cuiaba"]},{"value":"SA Western Standard Time","abbr":"SWST","offset":-4,"isdst":false,"text":"(UTC-04:00) Georgetown, La Paz, Manaus, San Juan","utc":["America/Anguilla","America/Antigua","America/Aruba","America/Barbados","America/Blanc-Sablon","America/Boa_Vista","America/Curacao","America/Dominica","America/Grand_Turk","America/Grenada","America/Guadeloupe","America/Guyana","America/Kralendijk","America/La_Paz","America/Lower_Princes","America/Manaus","America/Marigot","America/Martinique","America/Montserrat","America/Port_of_Spain","America/Porto_Velho","America/Puerto_Rico","America/Santo_Domingo","America/St_Barthelemy","America/St_Kitts","America/St_Lucia","America/St_Thomas","America/St_Vincent","America/Tortola","Etc/GMT+4"]},{"value":"Pacific SA Standard Time","abbr":"PSST","offset":-4,"isdst":false,"text":"(UTC-04:00) Santiago","utc":["America/Santiago","Antarctica/Palmer"]},{"value":"Newfoundland Standard Time","abbr":"NDT","offset":-2.5,"isdst":true,"text":"(UTC-03:30) Newfoundland","utc":["America/St_Johns"]},{"value":"E. South America Standard Time","abbr":"ESAST","offset":-3,"isdst":false,"text":"(UTC-03:00) Brasilia","utc":["America/Sao_Paulo"]},{"value":"Argentina Standard Time","abbr":"AST","offset":-3,"isdst":false,"text":"(UTC-03:00) Buenos Aires","utc":["America/Argentina/La_Rioja","America/Argentina/Rio_Gallegos","America/Argentina/Salta","America/Argentina/San_Juan","America/Argentina/San_Luis","America/Argentina/Tucuman","America/Argentina/Ushuaia","America/Buenos_Aires","America/Catamarca","America/Cordoba","America/Jujuy","America/Mendoza"]},{"value":"SA Eastern Standard Time","abbr":"SEST","offset":-3,"isdst":false,"text":"(UTC-03:00) Cayenne, Fortaleza","utc":["America/Araguaina","America/Belem","America/Cayenne","America/Fortaleza","America/Maceio","America/Paramaribo","America/Recife","America/Santarem","Antarctica/Rothera","Atlantic/Stanley","Etc/GMT+3"]},{"value":"Greenland Standard Time","abbr":"GDT","offset":-2,"isdst":true,"text":"(UTC-03:00) Greenland","utc":["America/Godthab"]},{"value":"Montevideo Standard Time","abbr":"MST","offset":-3,"isdst":false,"text":"(UTC-03:00) Montevideo","utc":["America/Montevideo"]},{"value":"Bahia Standard Time","abbr":"BST","offset":-3,"isdst":false,"text":"(UTC-03:00) Salvador","utc":["America/Bahia"]},{"value":"UTC-02","abbr":"U","offset":-2,"isdst":false,"text":"(UTC-02:00) Coordinated Universal Time-02","utc":["America/Noronha","Atlantic/South_Georgia","Etc/GMT+2"]},{"value":"Mid-Atlantic Standard Time","abbr":"MDT","offset":-1,"isdst":true,"text":"(UTC-02:00) Mid-Atlantic - Old"},{"value":"Azores Standard Time","abbr":"ADT","offset":0,"isdst":true,"text":"(UTC-01:00) Azores","utc":["America/Scoresbysund","Atlantic/Azores"]},{"value":"Cape Verde Standard Time","abbr":"CVST","offset":-1,"isdst":false,"text":"(UTC-01:00) Cape Verde Is.","utc":["Atlantic/Cape_Verde","Etc/GMT+1"]},{"value":"Morocco Standard Time","abbr":"MDT","offset":1,"isdst":true,"text":"(UTC) Casablanca","utc":["Africa/Casablanca","Africa/El_Aaiun"]},{"value":"UTC","abbr":"CUT","offset":0,"isdst":false,"text":"(UTC) Coordinated Universal Time","utc":["America/Danmarkshavn","Etc/GMT"]},{"value":"GMT Standard Time","abbr":"GDT","offset":1,"isdst":true,"text":"(UTC) Dublin, Edinburgh, Lisbon, London","utc":["Atlantic/Canary","Atlantic/Faeroe","Atlantic/Madeira","Europe/Dublin","Europe/Guernsey","Europe/Isle_of_Man","Europe/Jersey","Europe/Lisbon","Europe/London"]},{"value":"Greenwich Standard Time","abbr":"GST","offset":0,"isdst":false,"text":"(UTC) Monrovia, Reykjavik","utc":["Africa/Abidjan","Africa/Accra","Africa/Bamako","Africa/Banjul","Africa/Bissau","Africa/Conakry","Africa/Dakar","Africa/Freetown","Africa/Lome","Africa/Monrovia","Africa/Nouakchott","Africa/Ouagadougou","Africa/Sao_Tome","Atlantic/Reykjavik","Atlantic/St_Helena"]},{"value":"W. Europe Standard Time","abbr":"WEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna","utc":["Arctic/Longyearbyen","Europe/Amsterdam","Europe/Andorra","Europe/Berlin","Europe/Busingen","Europe/Gibraltar","Europe/Luxembourg","Europe/Malta","Europe/Monaco","Europe/Oslo","Europe/Rome","Europe/San_Marino","Europe/Stockholm","Europe/Vaduz","Europe/Vatican","Europe/Vienna","Europe/Zurich"]},{"value":"Central Europe Standard Time","abbr":"CEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague","utc":["Europe/Belgrade","Europe/Bratislava","Europe/Budapest","Europe/Ljubljana","Europe/Podgorica","Europe/Prague","Europe/Tirane"]},{"value":"Romance Standard Time","abbr":"RDT","offset":2,"isdst":true,"text":"(UTC+01:00) Brussels, Copenhagen, Madrid, Paris","utc":["Africa/Ceuta","Europe/Brussels","Europe/Copenhagen","Europe/Madrid","Europe/Paris"]},{"value":"Central European Standard Time","abbr":"CEDT","offset":2,"isdst":true,"text":"(UTC+01:00) Sarajevo, Skopje, Warsaw, Zagreb","utc":["Europe/Sarajevo","Europe/Skopje","Europe/Warsaw","Europe/Zagreb"]},{"value":"W. Central Africa Standard Time","abbr":"WCAST","offset":1,"isdst":false,"text":"(UTC+01:00) West Central Africa","utc":["Africa/Algiers","Africa/Bangui","Africa/Brazzaville","Africa/Douala","Africa/Kinshasa","Africa/Lagos","Africa/Libreville","Africa/Luanda","Africa/Malabo","Africa/Ndjamena","Africa/Niamey","Africa/Porto-Novo","Africa/Tunis","Etc/GMT-1"]},{"value":"Namibia Standard Time","abbr":"NST","offset":1,"isdst":false,"text":"(UTC+01:00) Windhoek","utc":["Africa/Windhoek"]},{"value":"GTB Standard Time","abbr":"GDT","offset":3,"isdst":true,"text":"(UTC+02:00) Athens, Bucharest","utc":["Asia/Nicosia","Europe/Athens","Europe/Bucharest","Europe/Chisinau"]},{"value":"Middle East Standard Time","abbr":"MEDT","offset":3,"isdst":true,"text":"(UTC+02:00) Beirut","utc":["Asia/Beirut"]},{"value":"Egypt Standard Time","abbr":"EST","offset":2,"isdst":false,"text":"(UTC+02:00) Cairo","utc":["Africa/Cairo"]},{"value":"Syria Standard Time","abbr":"SDT","offset":3,"isdst":true,"text":"(UTC+02:00) Damascus","utc":["Asia/Damascus"]},{"value":"E. Europe Standard Time","abbr":"EEDT","offset":3,"isdst":true,"text":"(UTC+02:00) E. Europe"},{"value":"South Africa Standard Time","abbr":"SAST","offset":2,"isdst":false,"text":"(UTC+02:00) Harare, Pretoria","utc":["Africa/Blantyre","Africa/Bujumbura","Africa/Gaborone","Africa/Harare","Africa/Johannesburg","Africa/Kigali","Africa/Lubumbashi","Africa/Lusaka","Africa/Maputo","Africa/Maseru","Africa/Mbabane","Etc/GMT-2"]},{"value":"FLE Standard Time","abbr":"FDT","offset":3,"isdst":true,"text":"(UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius","utc":["Europe/Helsinki","Europe/Kiev","Europe/Mariehamn","Europe/Riga","Europe/Sofia","Europe/Tallinn","Europe/Uzhgorod","Europe/Vilnius","Europe/Zaporozhye"]},{"value":"Turkey Standard Time","abbr":"TDT","offset":3,"isdst":false,"text":"(UTC+03:00) Istanbul","utc":["Europe/Istanbul"]},{"value":"Israel Standard Time","abbr":"JDT","offset":3,"isdst":true,"text":"(UTC+02:00) Jerusalem","utc":["Asia/Jerusalem"]},{"value":"Libya Standard Time","abbr":"LST","offset":2,"isdst":false,"text":"(UTC+02:00) Tripoli","utc":["Africa/Tripoli"]},{"value":"Jordan Standard Time","abbr":"JST","offset":3,"isdst":false,"text":"(UTC+03:00) Amman","utc":["Asia/Amman"]},{"value":"Arabic Standard Time","abbr":"AST","offset":3,"isdst":false,"text":"(UTC+03:00) Baghdad","utc":["Asia/Baghdad"]},{"value":"Kaliningrad Standard Time","abbr":"KST","offset":3,"isdst":false,"text":"(UTC+03:00) Kaliningrad, Minsk","utc":["Europe/Kaliningrad","Europe/Minsk"]},{"value":"Arab Standard Time","abbr":"AST","offset":3,"isdst":false,"text":"(UTC+03:00) Kuwait, Riyadh","utc":["Asia/Aden","Asia/Bahrain","Asia/Kuwait","Asia/Qatar","Asia/Riyadh"]},{"value":"E. Africa Standard Time","abbr":"EAST","offset":3,"isdst":false,"text":"(UTC+03:00) Nairobi","utc":["Africa/Addis_Ababa","Africa/Asmera","Africa/Dar_es_Salaam","Africa/Djibouti","Africa/Juba","Africa/Kampala","Africa/Khartoum","Africa/Mogadishu","Africa/Nairobi","Antarctica/Syowa","Etc/GMT-3","Indian/Antananarivo","Indian/Comoro","Indian/Mayotte"]},{"value":"Iran Standard Time","abbr":"IDT","offset":4.5,"isdst":true,"text":"(UTC+03:30) Tehran","utc":["Asia/Tehran"]},{"value":"Arabian Standard Time","abbr":"AST","offset":4,"isdst":false,"text":"(UTC+04:00) Abu Dhabi, Muscat","utc":["Asia/Dubai","Asia/Muscat","Etc/GMT-4"]},{"value":"Azerbaijan Standard Time","abbr":"ADT","offset":5,"isdst":true,"text":"(UTC+04:00) Baku","utc":["Asia/Baku"]},{"value":"Russian Standard Time","abbr":"RST","offset":4,"isdst":false,"text":"(UTC+04:00) Moscow, St. Petersburg, Volgograd","utc":["Europe/Moscow","Europe/Samara","Europe/Simferopol","Europe/Volgograd"]},{"value":"Mauritius Standard Time","abbr":"MST","offset":4,"isdst":false,"text":"(UTC+04:00) Port Louis","utc":["Indian/Mahe","Indian/Mauritius","Indian/Reunion"]},{"value":"Georgian Standard Time","abbr":"GST","offset":4,"isdst":false,"text":"(UTC+04:00) Tbilisi","utc":["Asia/Tbilisi"]},{"value":"Caucasus Standard Time","abbr":"CST","offset":4,"isdst":false,"text":"(UTC+04:00) Yerevan","utc":["Asia/Yerevan"]},{"value":"Afghanistan Standard Time","abbr":"AST","offset":4.5,"isdst":false,"text":"(UTC+04:30) Kabul","utc":["Asia/Kabul"]},{"value":"West Asia Standard Time","abbr":"WAST","offset":5,"isdst":false,"text":"(UTC+05:00) Ashgabat, Tashkent","utc":["Antarctica/Mawson","Asia/Aqtau","Asia/Aqtobe","Asia/Ashgabat","Asia/Dushanbe","Asia/Oral","Asia/Samarkand","Asia/Tashkent","Etc/GMT-5","Indian/Kerguelen","Indian/Maldives"]},{"value":"Pakistan Standard Time","abbr":"PST","offset":5,"isdst":false,"text":"(UTC+05:00) Islamabad, Karachi","utc":["Asia/Karachi"]},{"value":"India Standard Time","abbr":"IST","offset":5.5,"isdst":false,"text":"(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi","utc":["Asia/Kolkata"]},{"value":"Sri Lanka Standard Time","abbr":"SLST","offset":5.5,"isdst":false,"text":"(UTC+05:30) Sri Jayawardenepura","utc":["Asia/Colombo"]},{"value":"Nepal Standard Time","abbr":"NST","offset":5.75,"isdst":false,"text":"(UTC+05:45) Kathmandu","utc":["Asia/Katmandu"]},{"value":"Central Asia Standard Time","abbr":"CAST","offset":6,"isdst":false,"text":"(UTC+06:00) Astana","utc":["Antarctica/Vostok","Asia/Almaty","Asia/Bishkek","Asia/Qyzylorda","Asia/Urumqi","Etc/GMT-6","Indian/Chagos"]},{"value":"Bangladesh Standard Time","abbr":"BST","offset":6,"isdst":false,"text":"(UTC+06:00) Dhaka","utc":["Asia/Dhaka","Asia/Thimphu"]},{"value":"Ekaterinburg Standard Time","abbr":"EST","offset":6,"isdst":false,"text":"(UTC+06:00) Ekaterinburg","utc":["Asia/Yekaterinburg"]},{"value":"Myanmar Standard Time","abbr":"MST","offset":6.5,"isdst":false,"text":"(UTC+06:30) Yangon (Rangoon)","utc":["Asia/Rangoon","Indian/Cocos"]},{"value":"SE Asia Standard Time","abbr":"SAST","offset":7,"isdst":false,"text":"(UTC+07:00) Bangkok, Hanoi, Jakarta","utc":["Antarctica/Davis","Asia/Bangkok","Asia/Hovd","Asia/Jakarta","Asia/Phnom_Penh","Asia/Pontianak","Asia/Saigon","Asia/Vientiane","Etc/GMT-7","Indian/Christmas"]},{"value":"N. Central Asia Standard Time","abbr":"NCAST","offset":7,"isdst":false,"text":"(UTC+07:00) Novosibirsk","utc":["Asia/Novokuznetsk","Asia/Novosibirsk","Asia/Omsk"]},{"value":"China Standard Time","abbr":"CST","offset":8,"isdst":false,"text":"(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi","utc":["Asia/Hong_Kong","Asia/Macau","Asia/Shanghai"]},{"value":"North Asia Standard Time","abbr":"NAST","offset":8,"isdst":false,"text":"(UTC+08:00) Krasnoyarsk","utc":["Asia/Krasnoyarsk"]},{"value":"Singapore Standard Time","abbr":"MPST","offset":8,"isdst":false,"text":"(UTC+08:00) Kuala Lumpur, Singapore","utc":["Asia/Brunei","Asia/Kuala_Lumpur","Asia/Kuching","Asia/Makassar","Asia/Manila","Asia/Singapore","Etc/GMT-8"]},{"value":"W. Australia Standard Time","abbr":"WAST","offset":8,"isdst":false,"text":"(UTC+08:00) Perth","utc":["Antarctica/Casey","Australia/Perth"]},{"value":"Taipei Standard Time","abbr":"TST","offset":8,"isdst":false,"text":"(UTC+08:00) Taipei","utc":["Asia/Taipei"]},{"value":"Ulaanbaatar Standard Time","abbr":"UST","offset":8,"isdst":false,"text":"(UTC+08:00) Ulaanbaatar","utc":["Asia/Choibalsan","Asia/Ulaanbaatar"]},{"value":"North Asia East Standard Time","abbr":"NAEST","offset":9,"isdst":false,"text":"(UTC+09:00) Irkutsk","utc":["Asia/Irkutsk"]},{"value":"Tokyo Standard Time","abbr":"TST","offset":9,"isdst":false,"text":"(UTC+09:00) Osaka, Sapporo, Tokyo","utc":["Asia/Dili","Asia/Jayapura","Asia/Tokyo","Etc/GMT-9","Pacific/Palau"]},{"value":"Korea Standard Time","abbr":"KST","offset":9,"isdst":false,"text":"(UTC+09:00) Seoul","utc":["Asia/Pyongyang","Asia/Seoul"]},{"value":"Cen. Australia Standard Time","abbr":"CAST","offset":9.5,"isdst":false,"text":"(UTC+09:30) Adelaide","utc":["Australia/Adelaide","Australia/Broken_Hill"]},{"value":"AUS Central Standard Time","abbr":"ACST","offset":9.5,"isdst":false,"text":"(UTC+09:30) Darwin","utc":["Australia/Darwin"]},{"value":"E. Australia Standard Time","abbr":"EAST","offset":10,"isdst":false,"text":"(UTC+10:00) Brisbane","utc":["Australia/Brisbane","Australia/Lindeman"]},{"value":"AUS Eastern Standard Time","abbr":"AEST","offset":10,"isdst":false,"text":"(UTC+10:00) Canberra, Melbourne, Sydney","utc":["Australia/Melbourne","Australia/Sydney"]},{"value":"West Pacific Standard Time","abbr":"WPST","offset":10,"isdst":false,"text":"(UTC+10:00) Guam, Port Moresby","utc":["Antarctica/DumontDUrville","Etc/GMT-10","Pacific/Guam","Pacific/Port_Moresby","Pacific/Saipan","Pacific/Truk"]},{"value":"Tasmania Standard Time","abbr":"TST","offset":10,"isdst":false,"text":"(UTC+10:00) Hobart","utc":["Australia/Currie","Australia/Hobart"]},{"value":"Yakutsk Standard Time","abbr":"YST","offset":10,"isdst":false,"text":"(UTC+10:00) Yakutsk","utc":["Asia/Chita","Asia/Khandyga","Asia/Yakutsk"]},{"value":"Central Pacific Standard Time","abbr":"CPST","offset":11,"isdst":false,"text":"(UTC+11:00) Solomon Is., New Caledonia","utc":["Antarctica/Macquarie","Etc/GMT-11","Pacific/Efate","Pacific/Guadalcanal","Pacific/Kosrae","Pacific/Noumea","Pacific/Ponape"]},{"value":"Vladivostok Standard Time","abbr":"VST","offset":11,"isdst":false,"text":"(UTC+11:00) Vladivostok","utc":["Asia/Sakhalin","Asia/Ust-Nera","Asia/Vladivostok"]},{"value":"New Zealand Standard Time","abbr":"NZST","offset":12,"isdst":false,"text":"(UTC+12:00) Auckland, Wellington","utc":["Antarctica/McMurdo","Pacific/Auckland"]},{"value":"UTC+12","abbr":"U","offset":12,"isdst":false,"text":"(UTC+12:00) Coordinated Universal Time+12","utc":["Etc/GMT-12","Pacific/Funafuti","Pacific/Kwajalein","Pacific/Majuro","Pacific/Nauru","Pacific/Tarawa","Pacific/Wake","Pacific/Wallis"]},{"value":"Fiji Standard Time","abbr":"FST","offset":12,"isdst":false,"text":"(UTC+12:00) Fiji","utc":["Pacific/Fiji"]},{"value":"Magadan Standard Time","abbr":"MST","offset":12,"isdst":false,"text":"(UTC+12:00) Magadan","utc":["Asia/Anadyr","Asia/Kamchatka","Asia/Magadan","Asia/Srednekolymsk"]},{"value":"Kamchatka Standard Time","abbr":"KDT","offset":13,"isdst":true,"text":"(UTC+12:00) Petropavlovsk-Kamchatsky - Old"},{"value":"Tonga Standard Time","abbr":"TST","offset":13,"isdst":false,"text":"(UTC+13:00) Nuku'alofa","utc":["Etc/GMT-13","Pacific/Enderbury","Pacific/Fakaofo","Pacific/Tongatapu"]},{"value":"Samoa Standard Time","abbr":"SST","offset":13,"isdst":false,"text":"(UTC+13:00) Samoa","utc":["Pacific/Apia"]}];

        initController();

        function initController() {
            vm.loading = 0;
            load_repo_publish_times();

            for (var _cnt = 1; _cnt <= 31; _cnt++) {
                vm.days_of_month.push(_cnt);
            }

            $scope._task = obj_tasks[$state.current.name];

            switch($state.current.name) {
                case 'publish.on_demand':
                    load_publish_sites();
                    load_publish_sched();
                    vm.days_of_weeks_show = true;
                    vm.weekdays_show = false;
                    vm.days_of_month_show = false;
                    vm.weeks_of_month_show = false;

                    vm.form_fields.freqOption = vm.freq_option[0];  // 'Daily'
                    vm.form_fields.daysOfWeeks = vm.days_of_weeks[0];
                    vm.form_fields.dayOfMonth = vm.days_of_month[0];
                    vm.form_fields.weekOfMonth = vm.weeks_of_month[0];
                    vm.form_fields.time = vm.times[0];
                    vm.form_fields.timezone = vm.timezones[14];
                    vm.form_fields.id = -1;
                    break;
                case 'publish.last_dates':
                    load_publish_times_by_repo();
                    break;
                default:    // publish.list
                    load_publish_jobs();
                    load_mist_params();
            }

            for (var _index in vm.time_zones) {
                var time_zone = vm.time_zones[_index];
            }
            // vm.selected_day_show = false;
        }

        $scope.select_task = function(_task) {
            $scope._task = _task;
        };

        function load_publish_sched() {
            vm.loading += 1;
            PublishSchedService
                ._get_publishsched()
                .then(
                    function(results) {
                        $scope.publish_sched_list = results.publish_sched_list;

                        for (var _cnt_jobs in $scope.publish_sched_list) {
                            var _row = $scope.publish_sched_list[_cnt_jobs];
                            for (var _cnt_timezones in vm.timezones) {
                                var _timezone = vm.timezones[_cnt_timezones];
                                if (_row.timezone == _timezone.value) {
                                    $scope.publish_sched_list[_cnt_jobs]['offset'] = _timezone.offset;
                                    $scope.publish_sched_list[_cnt_jobs]['isdst'] = _timezone.isdst;
                                    break;
                                }
                            }
                        }
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_repo_publish_times() {
            vm.loading += 1;

            // expected fields from table repoPublishTimes
            var _fields = ['arfLast', 'benchmarkLast', 'cveLast', 'iavmLast', 'opattrLast', 'pluginLast'];
            RepoPublishTimesService
                ._get_repopublishtimes()
                .then(
                    function(results) {
                        // Add results.repo_publish_times if it's not defined and returned from API
                        if (results.repo_publish_times === undefined) {
                            results.repo_publish_times = {};
                            for (var _field in _fields) {
                                results.repo_publish_times[_fields[_field]] = 'None';
                            }
                        }
                        // Add individual values to results.repo_publish_times if they're not defined and returned from API
                        else {
                            for (var _field in _fields) {
                                if (results.repo_publish_times[_fields[_field]] === undefined) {
                                    results.repo_publish_times[_fields[_field]] = 'None';
                                }
                            }
                        }
                        $scope.repo_publish_times = results.repo_publish_times;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_publish_times_by_repo() {
            vm.loading += 1;
            RepoPublishTimesService
                ._get_publish_times_by_repo()
                .then(
                    function(results) {

                        // Remove "..Last" from all the repo keys.
                        for (var _repo in results.repo_publish_times) {
                            for (var _key in results.repo_publish_times[_repo]) {
                                var _new_key = _key.substring(0, _key.length - 4);
                                results.repo_publish_times[_repo][_new_key] = results.repo_publish_times[_repo][_key];
                                delete results.repo_publish_times[_repo][_key];
                            }
                        }
                        $scope.repo_publish_times_by_repo = results.repo_publish_times;
                        vm.loading -= 1;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_publish_jobs() {
            vm.loading += 1;
            PublishJobsService
                ._get_publishjobs()
                .then(
                    function(results) {
                        $scope.publish_jobs_list = results.publish_jobs_list;

                        // [kept for reference] [ES5] array forEach loop
                        // $scope.publish_jobs_list.forEach(function(_row, _index, _ref) {
                        //     if (_row.status == 'Completed') {
                        //         _ref[_index].filename = '<a href="#">' + _row.filename + '</a>';
                        //     }
                        // });

                        // [kept for reference] Displaying links in ui-grid cell
                        // $scope.column_names = [
                        //     {
                        //       "name": "Filename"
                        //       , "displayName": "Filename"
                        //       , "field": "filename"
                        //       , "width": 350
                        //       , cellTemplate: '<div><a href="#">{{row.entity.filename}}</a></div>'
                        //     },
                        //     {
                        //       "name": "PublishDate"
                        //       , "displayName": "Publish Date"
                        //       , "field": "finishTime"
                        //       , "width": 150
                        //       , "sort": {"direction": "desc", "priority": 0}
                        //     },
                        //     {
                        //       "name": "Status"
                        //       , "displayName": "Status"
                        //       , "field": "status"
                        //     },
                        //     {
                        //       "name": "PublishedBy"
                        //       , "displayName": "Published By"
                        //       , "field": "userName"
                        //     }
                        // ];
                        // $scope.grid_options = {
                        //     columnDefs: $scope.column_names
                        // };
                        // $scope.grid_options.data = results.publish_jobs_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_publish_sites() {
            vm.loading += 1;
            PublishSitesService
                ._get_publishsites()
                .then(
                    function(results) {
                        vm.publish_sites_list = results.publish_sites_list;
                        vm.publish_sites_list.unshift({'id':0,'location':'localhost','name':'localhost'});
                        vm.form_fields.selected_site = vm.publish_sites_list[0];    // setting default selection in here may be bad practice; didn't work when tried in init() - JWT 2 Mar 2017
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        $scope.delete_job = function(_id) {
            return PublishJobsService
                ._delete_publishjobs(_id)
                .then(
                      function(result) {
                        $scope.status = 'Deleted scheduled job.';
                        $scope.status_class = 'alert alert-success';
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                )
                .then(function() {
                    load_publish_sched();
                })
                .then(function() {
                    // clear status message after five seconds
                    $timeout(function() {
                        $scope.status = '';
                        $scope.status_class = '';
                    }, 5000);
                });
        };

        $scope.publish = function() {
            vm.form_fields.publishOptions = '';
            vm.form_fields.assetOptions = '';
            vm.user = ' --user ' + $localStorage.user.id;
            vm.site = ' --site "' + vm.form_fields.selected_site.location + '"';
            vm.options = vm.user + vm.site;
            vm.scan_options_checked = false;
            vm.asset_options_checked = false;

            vm.scan_options_checked = false;
            for (var _node in $scope.scan_options) {
                if ($scope.scan_options[_node]) {
                    vm.options += ' --' + _node;
                    vm.form_fields.publishOptions += ' --' + _node;
                    if (_node.substring(0,4) != 'all_') {
                        vm.scan_options_checked = true; // marked true if at least one scan result option is checked
                    }
                }
            }

            vm.asset_options_checked = false;
            for (var _node in $scope.asset_options) {
                if ($scope.asset_options[_node]) {
                    vm.options += ' --' + _node;
                    vm.form_fields.assetOptions += ' --' + _node;
                    if (_node.substring(0,4) != 'all_') {
                        vm.asset_options_checked = true;    // marked true if at least one tagged asset option is checked
                    }
                }
            }

            vm.form_fields['options'] = vm.options;
            vm.form_fields['destSite'] = vm.form_fields.selected_site.location;
            vm.form_fields['destSiteName'] = vm.form_fields.selected_site.name;
            vm.form_fields['user'] = $localStorage.user.username;

            if (!vm.scan_options_checked && !vm.asset_options_checked) {
                $scope.status = 'Please select one or more scan result or tagged asset options.';
                $scope.status_class = 'alert alert-warning';
                // clear status message after five seconds
                $timeout(function() {
                    $scope.status = '';
                    $scope.status_class = '';
                }, 5000);
            }
            else {
                return PublishJobsService
                    ._insert_publishjobs(vm.form_fields)
                    .then(
                          function(result) {
                            $scope.status = 'Executed publish ' + vm.form_fields.job_type + '.';
                            $scope.status_class = 'alert alert-success';
                          }
                        , function(err) {
                            $scope.status = 'Error loading data: ' + err.message;
                            vm.loading -= 1;
                          }
                    )
                    .then(function() {
                        load_publish_sched();
                    })
                    .then(function() {
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                            $scope.status_class = '';
                        }, 5000);
                    });
            }

        };

        function load_mist_params() {
            MistParamsService
                ._get_mist_params()
                .then(
                    function(results) {
                        var _mist_params = results.mist_params_list[0];
                        // $scope._mist_params = _mist_params;
                        $scope.assign_chunk_size = _mist_params.chunkSize;
                        $scope.assign_log_rollover = _mist_params.logsRollOverPeriod;
                        $scope.assign_pub_rollover = _mist_params.pubsRollOverPeriod;
                        $scope.assign_assets_refresh = _mist_params.scPullFreq;
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        vm.switch_job_type = function() {
            vm.form_fields.job_type = (vm.scheduled_job) ? 'on demand' : 'scheduled job';
        };

        function switch_freq() {
            var _freq = vm.form_fields.freqOption;
            switch (_freq) {
                case 'Weekly':
                    vm.days_of_weeks_show = false;
                    vm.weekdays_show = true;
                    vm.days_of_month_show = false;
                    vm.weeks_of_month_show = false;
                    vm.form_fields.daysOfWeeks = vm.weekdays[0];
                    break;
                case 'Monthly(Date)':
                    vm.days_of_weeks_show = false;
                    vm.weekdays_show = false;
                    vm.days_of_month_show = true;
                    vm.weeks_of_month_show = false;
                    break;
                case 'Monthly(Day)':
                    vm.days_of_weeks_show = false;
                    vm.weekdays_show = true;
                    vm.days_of_month_show = false;
                    vm.weeks_of_month_show = true;
                    vm.form_fields.daysOfWeeks = vm.weekdays[0];
                    break;
                default:
                    vm.days_of_weeks_show = true;
                    vm.weekdays_show = false;
                    vm.days_of_month_show = false;
                    vm.weeks_of_month_show = false;
                    vm.form_fields.daysOfWeeks = vm.days_of_weeks[0];
            }
        }

        // unchecks option checkboxes
        function reset_options() {
            for (var _item in $scope.asset_options) {
                $scope.asset_options[_item] = false;
            }
            for (var _item in $scope.scan_options) {
                $scope.scan_options[_item] = false;
            }
        }

        vm.switch_freq = function() {
            switch_freq();
        }

        $scope.update_job = function (_id) {
            for (var _cnt in $scope.publish_sched_list) {
                var _job = $scope.publish_sched_list[_cnt];
                if (_job.id == _id) {
                    vm.form_fields.id = _id;    // set ID
                    vm.form_fields.freqOption = _job.freqOption;    // set frequency
                    vm.form_fields.time = _job.time;    // set time
                    vm.form_fields.offset = _job.offset;
                    vm.form_fields.isdst = _job.isdst;

                    for (var _cnt2 in vm.publish_sites_list) {  // set location
                        var _site = vm.publish_sites_list[_cnt2];
                        if (_job.destSite == _site.location) {
                            vm.form_fields.selected_site = vm.publish_sites_list[_cnt2];
                            break;
                        }
                    }

                    // set options
                    reset_options();
                    var _asset_options = _job.assetOptions.trim().split(' ');
                    for (var _cnt2 in _asset_options) {
                        var _length = _asset_options[_cnt2].length;
                        var _asset_option = _asset_options[_cnt2].substring(2, _length);
                        $scope.asset_options[_asset_option] = true;
                    }

                    var _publish_options = _job.publishOptions.trim().split(' ');
                    for (var _cnt2 in _publish_options) {
                        var _length = _publish_options[_cnt2].length;
                        var _publish_option = _publish_options[_cnt2].substring(2, _length);
                        $scope.scan_options[_publish_option] = true;
                    }

                    // set schedule pulldowns
                    switch (_job.freqOption) {
                        case 'Weekly':
                            vm.form_fields.daysOfWeeks = _job.daysOfWeeks;
                            break;
                        case 'Monthly(Date)':
                            vm.form_fields.dayOfMonth = parseInt(_job.dayOfMonth);
                            break;
                        case 'Monthly(Day)':
                            vm.form_fields.weekOfMonth = _job.weekOfMonth;
                            vm.form_fields.daysOfWeeks = _job.daysOfWeeks;
                            break;
                        default:
                            vm.form_fields.daysOfWeeks = _job.daysOfWeeks;
                    }

                    // set timezone
                    for (var _cnt2 in vm.timezones) {
                        var _timezone = vm.timezones[_cnt2];
                        if (_timezone.value == _job.timezone) {
                            vm.form_fields.timezone = vm.timezones[_cnt2];
                            break;
                        }
                    }

                    break;
                }
            }
            switch_freq();
        };

        $scope.reset_form = function() {
            reset_options();
            vm.form_fields.selected_site = vm.publish_sites_list[0];
            vm.form_fields.id = -1;
            vm.form_fields.freqOption = vm.freq_option[0];
            vm.form_fields.daysOfWeeks = vm.days_of_weeks[0];
            vm.form_fields.time = vm.times[0];
            vm.form_fields.timezone = vm.timezones[14];
            switch_freq();
        };

        $scope.refresh_data = function() {
            load_publish_jobs();
        };

        $scope.reload_publish_last_dates = function() {
            load_publish_times_by_repo();
        };
    }
})();
