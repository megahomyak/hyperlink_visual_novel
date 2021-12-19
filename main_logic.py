import os

import aiohttp.web

import locations

app = aiohttp.web.Application()
router = aiohttp.web.RouteTableDef()


locations_dict = locations.make_locations_dict()


@router.get("/files/{filename}")
async def handle_file_request(request: aiohttp.web.Request):
    try:
        file = open(os.path.join("files", request.match_info["filename"]), "rb")
    except FileNotFoundError:
        raise aiohttp.web.HTTPNotFound()
    else:
        return aiohttp.web.Response(body=file)


@router.get("/")
async def handle_root_request(_: aiohttp.web.Request):
    raise aiohttp.web.HTTPFound("/locations/main")


a = 0


@router.get("/locations/{location_name}")
async def handle_location_request(request: aiohttp.web.Request):
    global a
    a += 1
    print(a)
    print(request.url)
    location_name = request.match_info["location_name"]
    try:
        location = locations_dict[location_name]
    except KeyError:
        return aiohttp.web.Response(
            body="Локация не найдена!"  # Location not found!
        )
    else:
        flags = (
            set(request.query_string.split("|"))
        ) if request.query_string else set()
        location_to_switch_to_name = None
        while True:
            for flag, location_name_ in location.flag_to_location_name:
                if flag in flags:
                    location = locations_dict[location_name_]
                    location_to_switch_to_name = location_name_
                    break
            else:
                break
        for flag in location.flags_to_add:
            flags.add(flag)
        for flag in location.flags_to_remove:
            try:
                flags.remove(flag)
            except KeyError:
                pass
        if location_to_switch_to_name:
            raise aiohttp.web.HTTPFound(
                locations.make_location_link(location_to_switch_to_name, flags)
            )
        print(location_name, flags)
        return aiohttp.web.Response(
            body=location.make_html(flags),
            content_type="text/html"
        )


app.add_routes(router)
aiohttp.web.run_app(app, host=locations.config.host, port=locations.config.port)
