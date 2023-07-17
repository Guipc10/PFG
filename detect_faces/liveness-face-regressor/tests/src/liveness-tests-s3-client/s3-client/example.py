
from comm_client import CommClient
import asyncio

async def main():
    cc = CommClient()
    request_id = "igorm_testes_comm"

    #example: getting pitch and yaw
    file = open('liveness_tests/instances/reais/t0/down_up_left_right_down.zip', 'rb').read()
    images = await cc.parse_zip_file(file)
    result = await cc.get_params(images, request_id)
    breakpoint()

if __name__ == "__main__":
    asyncio.run(main())