"""Upcoming community events presented on the website calendar."""

# Event dates and names are taken from the five latest supplied banners.
# The images show date ranges but no start times, so these are all-day entries.
EVENT_SCHEDULE: list[dict] = [
    {
        "id": "uma-orientation-2026",
        "kind": "event",
        "name": "วันปฐมนิเทศสาวม้าและเทรนเนอร์",
        "description": "กิจกรรมวันปฐมนิเทศสาวม้าและเทรนเนอร์ 24–25 ตุลาคม 2026",
        "date": "2026-10-24",
        "time": "00:00",
        "image_url": "/eventBanners/Orientation.webp",
    },
    {
        "id": "uma-radio-halloween-2026",
        "kind": "event",
        "name": "Uma Radio คลื่นสยองของสาวม้ารุ่นใหม่",
        "description": "กิจกรรม Halloween วันที่ 30–31 ตุลาคม 2026",
        "date": "2026-10-30",
        "time": "00:00",
        "image_url": "/eventBanners/Halloween_Event.webp",
    },
    {
        "id": "autumn-holiday-2026",
        "kind": "event",
        "name": "วันหยุดอำลากฤดูใบไม้ร่วง",
        "description": "กิจกรรมวันหยุดอำลากฤดูใบไม้ร่วง 15–21 พฤศจิกายน 2026",
        "date": "2026-11-15",
        "time": "00:00",
        "image_url": "/eventBanners/AutumeHoliday.webp",
    },
    {
        "id": "winter-music-festival-2026",
        "kind": "event",
        "name": "Winter Festival เทศกาลดนตรีท่ามกลางหนาว",
        "description": "เทศกาลดนตรีฤดูหนาว วันที่ 5–7 ธันวาคม 2026",
        "date": "2026-12-05",
        "time": "00:00",
        "image_url": "/eventBanners/WinterMusicFestival.webp",
    },
    {
        "id": "uma-christmas-2026",
        "kind": "event",
        "name": "Uma-ma Christmas เทศกาลคริสต์มาส",
        "description": "กิจกรรมคริสต์มาส วันที่ 24–31 ธันวาคม 2026",
        "date": "2026-12-24",
        "time": "00:00",
        "image_url": "/eventBanners/UmaChristmas.webp",
    },
]
