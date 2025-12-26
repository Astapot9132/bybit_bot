import math


def round_down(number, decimals=0):
  """
  Округляет число по недостатку до заданного количества знаков после запятой.
  """
  factor = 10 ** decimals
  return math.floor(number * factor) / factor
