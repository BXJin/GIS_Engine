from qgis.core import (
    QgsProject,
    QgsMapLayer,
)
from typing import Callable, List
from geon.utils import IterableUtils


def where(
    predicate: Callable[[QgsMapLayer], bool] = lambda layer: True,
) -> List[QgsMapLayer]:
    """
    주어진 조건(predicate)을 만족하는 모든 레이어를 반환.

    :param predicate: 레이어 필터링을 위한 함수 (기본값: 항상 True)
    :return: 조건을 만족하는 레이어 리스트
    """
    return [
        layer
        for layer in QgsProject.instance().mapLayers().values()
        if predicate(layer)
    ]


def get_layer_by_name(layer_name: str):
    """ """
    layers = where(lambda layer: layer.name() == layer_name)
    return IterableUtils.first(layers)
