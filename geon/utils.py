from typing import Iterable, Any, Optional

class IterableUtils:
    """반복 가능한(iterable) 객체를 다루는 유틸리티 클래스"""

    @staticmethod
    def first(iterable: Iterable[Any], default: Optional[Any] = None) -> Optional[Any]:
        """주어진 iterable에서 첫 번째 요소를 반환. 없으면 default 값 반환."""
        return next(iter(iterable), default)

    @staticmethod
    def last(iterable: Iterable[Any], default: Optional[Any] = None) -> Optional[Any]:
        """주어진 iterable에서 마지막 요소를 반환. 없으면 default 값 반환."""
        return iterable[-1] if iterable else default

    @staticmethod
    def without_first(iterable: Iterable[Any]) -> list:
        """첫 번째 요소를 제외한 나머지 리스트 반환"""
        return list(iterable)[1:]

    @staticmethod
    def without_last(iterable: Iterable[Any]) -> list:
        """마지막 요소를 제외한 나머지 리스트 반환"""
        return list(iterable)[:-1]
    

