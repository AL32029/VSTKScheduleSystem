import aiofiles


async def test_schedule_provider_use_case(
    schedule_parser_use_case, httpx_mock
):
    async with aiofiles.open("./tests/fixtures/schedule.html", "rb") as f:
        httpx_mock.add_response(
            method="GET",
            url="https://vgtk.by/schedule/lessons/day-tomorrow.php",
            content=await f.read(),
        )

    await schedule_parser_use_case.execute()
