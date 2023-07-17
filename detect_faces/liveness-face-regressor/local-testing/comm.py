import asyncio
import requests
import math
import threading
import backoff
import concurrent.futures
import json


def flat_list(t):
    return [item for sublist in t for item in sublist]


class LivenessComm(object):

    """
    Summary
        Superclass representing the base of Liveness communications
    Parameters
    ----------
        _url: str
            The url to communicate
        _name: str
            The name of the container
    """

    _instance = None
    _instance_lock = threading.Lock()

    # Make it singleton
    def __new__(cls, _url, _name, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super(LivenessComm, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, _url, _name, *args, **kwargs):
        self._url = _url
        self._name = _name

        self._loop = asyncio.get_event_loop()

    def _get_batch_size(self, _size):
        """
        Summary
            Returns a batch_size and number of workers
            to make parallel batch requests
        Parameters
        ----------
            _size: int
                The size of frames list
        Returns
        -------
            batch_size: int
            n_workers: int
        """

        if _size < 40:
            return 40, 1
        elif _size > 40 and _size < 90:
            return math.ceil(_size / 2), 2
        else:
            return math.ceil(_size / 3), 3

    def _post_json(self, url, request_id, files, key="images"):
        """
        Summary
            Simple post request sending json
        Parameters
        ----------
            url: str
            request_id: str
            files: List[bytes]
        Returns
        -------
            response: Response
        """

        files_list = [{key: file} for file in files]
        return requests.post(
            url, json=files_list, headers={"Param-Request-Id": request_id}
        )

    def _post_mp(self, url, request_id, files, key="images"):

        """
        Summary
            Simple post request sending mp\\form-data
        Parameters
        ----------
            url: str
            request_id: str
            files: List[bytes]
        Returns
        -------
            response: Response
        """

        files_list = [(key, file) for file in files]
        return requests.post(
            url, files=files_list, headers={"Param-Request-Id": request_id}
        )

    def _post_mp_ec(
        self, url, request_id, images, bboxes, key1="images", key2="bboxes"
    ):

        """
        Summary
            Simple post request sending mp\\form-data
        Parameters
        ----------
            url: str
            request_id: str
            files: List[bytes]
            bboxes: List[List[]]
        Returns
        -------
            response: Response
        """

        data = {"images": images, "bboxes": bboxes}
        payload = json.dumps(data)

        return requests.post(
            url,
            data=payload,
            headers={
                "Param-Request-Id": request_id,
                "content-type": "application/json",
            },
        )

    async def _batch_request(self, images, request_id):
        """
        Summary
           Divides images array in batches and parallelize requests
           containing these batches.
        Parameters
        ----------
            images: List[bytes]
            request_id: str
        Returns
        -------
            response: Response
        """
        batch_size, n_workers = self._get_batch_size(len(images))
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=n_workers)
        response = await asyncio.gather(
            *[
                self._loop.run_in_executor(
                    executor,
                    self._post_mp,
                    self._url,
                    request_id,
                    images[idx : idx + batch_size],
                )
                for idx in range(0, len(images), batch_size)
            ]
        )
        return response

    def get_event_loop(self):
        return self._loop

    def set_event_loop(self, loop):
        self._loop = loop


class FaceRegressorComm(LivenessComm):

    """
    Summary
        Class representing FaceRegressor communications
    Parameters
    ----------
        url: str
        name: str
    """

    def __init__(self, url, name=None):
        super().__init__(_url=url, _name=name)

    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=5
    )
    async def get_images_roi(self, images, request_id):

        """
        Summary
            Makes request and standardize response
        Parameters
        ----------
            images: List[bytes]
            request_id: str

        Returns
        -------
            response_standard: FaceRegressorResponse
        """

        response = await self._batch_request(images, request_id)
        [r.raise_for_status() for r in response]
        response_standard = FaceRegressorResponse()
        response_standard.standardize(response)

        return response_standard


class NewFaceRegressorComm(LivenessComm):

    """
    Summary
        Class representing FaceRegressor communications
    Parameters
    ----------
        url: str
        name: str
    """

    def __init__(self, url, name=None):
        super().__init__(_url=url, _name=name)

    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=5
    )
    async def get_images_roi(self, images, request_id):

        """
        Summary
            Makes request and standardize response
        Parameters
        ----------
            images: List[bytes]
            request_id: str

        Returns
        -------
            response_standard: FaceRegressorResponse
        """

        response = await self._batch_request(images, request_id)
        [r.raise_for_status() for r in response]
        response_standard = NewFaceRegressorResponse()
        response_standard.standardize(response)

        return response_standard


class NewFaceRegressorResponse(object):
    def __init__(self, args=None):
        self.args: Dict[str, str] = args
        self.images: List[bytes] = None
        self.keypoints: List[List[tuple]] = None
        self.bboxes: List[List[tuple]] = None
        self.images_n: List[bytes] = None
        self.scores: List[float] = None
        self.has_obstruction: List[bool] = None
        self.remained_frames_ratio: float = None
        self.filtering_successfull: bool = True

    def _set_obstructions(self, response):
        self.has_obstruction = response.get("has_obstruction", None)

    def _set_scores(self, response):
        self.scores = response.get("scores", None)

    def _set_images(self, response):
        self.images = response.get("images", None)

    def _set_images_n(self, response):
        self.images_n = response.get("images_n", None)

    def _set_keypoints(self, response):
        self.keypoints = response.get("keypoints", None)

    def _set_bboxes(self, response):
        self.bboxes = response.get("bboxes", None)

    def _remove_low_scores(
        self, confidence_threshold=0.5, remained_frames_threshold=0.5
    ):
        idxs = []
        for idx, score in enumerate(self.scores):
            if float(score) < confidence_threshold:
                idxs.append(idx)

        # Check if a sufficient number of frames remained
        # If too few remained, remove all frames from response
        self.remained_frames_ratio = 1 - (len(idxs) / (len(self.scores) + 1))
        if self.remained_frames_ratio < remained_frames_threshold:
            idxs = range(len(self.scores))
            self.filtering_successfull = False

        self.keypoints = self._filter_by_idxs(self.keypoints, idxs)
        self.bboxes = self._filter_by_idxs(self.bboxes, idxs)
        self.images = self._filter_by_idxs(self.images, idxs)
        self.images_n = self._filter_by_idxs(self.images_n, idxs)
        self.scores = self._filter_by_idxs(self.scores, idxs)

    def _filter_by_idxs(self, lst, idxs):
        return [l for idx, l in enumerate(lst) if idx not in idxs]

    def _parse_response(self, response):
        images_lst = []
        bboxes_lst = []
        kps_lst = []
        images_n_lst = []
        scores_lst = []
        obstructions_lst = []
        for r in response:
            resp = r.json()
            if len(resp) > 0:
                images = resp[0]["images_cropped"]
                bboxes = resp[0]["bboxes"]
                kps = resp[0]["keypoints"]
                images_n = resp[0]["images_n"]
                scores = resp[0]["scores"]
                has_obstruction = resp[0]["has_obstruction"]

                images_lst.append(images)
                bboxes_lst.append(bboxes)
                kps_lst.append(kps)
                images_n_lst.append(images_n)
                scores_lst.append(scores)
                obstructions_lst.append(has_obstruction)

        return dict(
            images=flat_list(images_lst),
            bboxes=flat_list(bboxes_lst),
            keypoints=flat_list(kps_lst),
            images_n=flat_list(images_n_lst),
            scores=flat_list(scores_lst),
            has_obstruction=flat_list(obstructions_lst),
        )

    def standardize(self, response):
        response = self._parse_response(response)
        self._set_obstructions(response)
        self._set_images(response)
        self._set_bboxes(response)
        self._set_keypoints(response)
        self._set_images_n(response)
        self._set_scores(response)

        self._remove_low_scores()

    def get_faces_info(self):
        return dict(
            images_n=self.images_n, bboxes=self.bboxes, keypoints=self.keypoints
        )


class FaceRegressorResponse(object):
    def __init__(self, args=None):
        self.args: Dict[str, str] = args
        self.images: List[bytes] = None
        self.keypoints: List[List[tuple]] = None
        self.bboxes: List[List[tuple]] = None
        self.images_n: List[bytes] = None
        self.scores: List[float] = None
        self.has_obstruction: List[bool] = None
        self.remained_frames_ratio: float = None
        self.filtering_successfull: bool = True

    def _set_obstructions(self, response):
        self.has_obstruction = response.get("has_obstruction", None)

    def _set_scores(self, response):
        self.scores = response.get("scores", None)

    def _set_images(self, response):
        self.images = response.get("images", None)

    def _set_images_n(self, response):
        self.images_n = response.get("images_n", None)

    def _set_keypoints(self, response):
        self.keypoints = response.get("keypoints", None)

    def _set_bboxes(self, response):
        self.bboxes = response.get("bboxes", None)

    def _remove_low_scores(
        self, confidence_threshold=0.75, remained_frames_threshold=0.5
    ):
        idxs = []
        for idx, score in enumerate(self.scores):
            if float(score) < confidence_threshold:
                idxs.append(idx)

        # Check if a sufficient number of frames remained
        # If too few remained, remove all frames from response
        self.remained_frames_ratio = 1 - (len(idxs) / (len(self.scores) + 1))
        if self.remained_frames_ratio < remained_frames_threshold:
            idxs = range(len(self.scores))
            self.filtering_successfull = False

        self.keypoints = self._filter_by_idxs(self.keypoints, idxs)
        self.bboxes = self._filter_by_idxs(self.bboxes, idxs)
        self.images = self._filter_by_idxs(self.images, idxs)
        self.images_n = self._filter_by_idxs(self.images_n, idxs)
        self.scores = self._filter_by_idxs(self.scores, idxs)

    def _filter_by_idxs(self, lst, idxs):
        return [l for idx, l in enumerate(lst) if idx not in idxs]

    def _parse_response(self, response):
        images_lst = []
        bboxes_lst = []
        kps_lst = []
        images_n_lst = []
        scores_lst = []
        obstructions_lst = []
        for r in response:
            resp = r.json()
            if len(resp) > 0:
                images = resp[0]["images"]
                images = [image for image in images if image is not None]
                images.sort(key=lambda x: x[1], reverse=False)
                images_r = [image[0] for image in images]
                bboxes = [image[2] for image in images]
                kps = [image[3] for image in images]
                images_n = [image[4] for image in images]
                scores = [image[5] for image in images]
                has_obstruction = [image[6] for image in images]

                images_lst.append(images_r)
                bboxes_lst.append(bboxes)
                kps_lst.append(kps)
                images_n_lst.append(images_n)
                scores_lst.append(scores)
                obstructions_lst.append(has_obstruction)
        return dict(
            images=flat_list(images_lst),
            bboxes=flat_list(bboxes_lst),
            keypoints=flat_list(kps_lst),
            images_n=flat_list(images_n_lst),
            scores=flat_list(scores_lst),
            has_obstruction=flat_list(obstructions_lst),
        )

    def standardize(self, response):
        response = self._parse_response(response)
        self._set_obstructions(response)
        self._set_images(response)
        self._set_bboxes(response)
        self._set_keypoints(response)
        self._set_images_n(response)
        self._set_scores(response)

        self._remove_low_scores()
