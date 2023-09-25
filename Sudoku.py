from typing import *
from utils import cross, chunk_string_by_len

ROWS = 'ABCDEFGHI'
COLS = '123456789'

boxes = cross(ROWS, COLS)
row_units = [cross(r,COLS) for r in ROWS]
col_units = [cross(ROWS,c) for c in COLS]
square_units = [cross(r,c) for r in chunk_string_by_len(ROWS) for c in chunk_string_by_len(COLS)]
unit_list = row_units + col_units + square_units

def get_puzzle() -> str:
    """Возвращает головоломку.

    Returns:
        str: Возвращает строку головоломки.
    """
    return '..36...8.1..4..9....517..4...6..2....2...57..8...6...2..1.9..6....5....9......3.7'

def grid_values(puzzle:str,boxes:List[str],replace:bool=True) -> Dict[str,str]:
    """Эта функция сопоставляет каждую единицу головоломки с соответствующей коробкой.
    Args:
        puzzle (str): Строка головоломки
        boxes (List[str]): Список коробочных единиц
        replace (bool) : Возможность замены точек цифрами от 1 до 9. По умолчанию установлено значение True.
    Returns:
        Dict[str,str]: Словарь коробочных единиц с его значением головоломки.
    """
    assert len(puzzle) == 81
    
    return {key : ( '123456789' if value =='.' and replace else value) for key,value in zip(boxes,puzzle)}


def display_sudoku(p_values:Dict[str,str])  -> None:
    """Эта функция отображает словарь в правильном формате сетки.
    Args:
        p_values (Dict[str,str]): Словарь головоломки с номером коробки и значением.
    
    """
    assert (len(p_values) == 81),"В словаре должно быть 81 значение."
    
    max_len=len(max(list(p_values.values()),key=len))+2 #максимальная длина среди всех коробок
    
    print(f"\n{' SUDOKU '.center(max_len*9,'=')}\n")
    list_puzzle = list(p_values.items())
    
    n=9 #шаг
    for i in range(0,len(p_values),n):
        row=''
        for index,box in enumerate(list_puzzle[i:i+n]):
            if (index > 1 and index < 9) and index % 3 == 0 :
                row +='|'  #добавить трубу посередине
            row +=box[1].center(max_len)
            
        print(row,'\n')
        if i == 18 or i== 45 :  #добавить декоративную линию посередине
            pt='-'*(max_len*3) #крачка
            print('+'.join([pt,pt,pt]),'\n')
            
def find_peers(box:str) -> List[str]:
    """Эта функция возвращает одноранговые узлы коробки.
    Args:
        box (str): Коробка
    
    Returns:
        List[str]: Список пиров для данного ящика.
    """
    
    peers_list=[list for list in unit_list if box in list]
    peers = list(set([item for sub_list in peers_list for item in sub_list if item !=box]))
    return peers
     
def eliminate(grids:Dict[str,str]) -> Dict[str,str]:
    """Эта функция удаляет значения из блоков временных блоков (со значениями 1-9), если
        который присутствует в одноранговых узлах этого ящика.
    Args:
        grids (Dict[str,str]): Словарь единиц судоку
        
    Returns:
        grids (Dict[str,str]): Словарь единиц судоку с исключенными значениями.
    """
    for key,value in grids.items():
        if len(value) > 1:
            peers = find_peers(key)
            peers_values = [grids.get(k) for k in peers if len(grids.get(k))==1]
            for v in peers_values:
                value=value.replace(v,"")
            grids[key]=value
    return grids

def only_choice(grids:Dict[str,str]) -> Dict[str,str]:
    """Эта функция заменяет исключенные квадратные блоки только значением выбора.
        с в единице.

    Args:
        grids (Dict[str,str]): Словарь единиц судоку

    Returns:
        grids (Dict[str,str]): Словарь единиц судоку с заменой только значений.
    """
    for unit in unit_list:
        for digit in '123456789':
            d_places = [box for box in unit if digit in grids[box]]
            if len(d_places) == 1:
                grids[d_places[0]] = digit
    return grids
    
def reduce_puzzle(grids:Dict[str,str]) -> Union[Dict[str,str],bool]:
    """Эта функция сводит нерешенные единицы поля к одному значению с повторным удалением и сокращением.

    Args:
        grids (Dict[str,str]): Словарь единиц судоку

    Returns:
        grids (Dict[str,str]): Словарь единиц судоку с заменой только значений.
        solved (bool) : Логическое значение, указывающее, решена головоломка или нет.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([value for value in grids.values() if len(value)==1])#всего единиц с одним значением
        grids = eliminate(grids)
        grids = only_choice(grids)
        solved_values_after = len([value for value in grids.values() if len(value)==1])#всего единиц с одним значением
        stalled = solved_values_before == solved_values_after
        if len([box for box in grids.keys() if len(grids[box]) == 0]):
            return False 
    return grids

def search(values:Dict[str,str])->Dict[str,str]:
    "Используя поиск в глубину и распространение, создайте дерево поиска и решите судоку."
    # Сначала уменьшите головоломку, используя предыдущую функцию
    values = reduce_puzzle(values)
    if values is False:
        return False ## Ошибка ранее
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Решено!
    
    # Выберите один из незаполненных квадратов с наименьшим количеством возможностей
    # проверяет минимальные значения в списке кортежей
    n,k =  min((len(v),k) for k,v in values.items() if len(v)>1)
    
    # Теперь используйте рекурсию для решения каждого из полученных судоку, и если один из них возвращает значение (не False), верните этот ответ!
    for value in values[k]:
        new_sudoku=values.copy()
        new_sudoku[k]=value
        attempt = search(new_sudoku,)
        if attempt:
            return attempt
        
def check_if_sudoku_solved(grids:Dict[str,str]) -> bool:
    for unit in unit_list:
        unit_values_sum = sum([int(grids.get(k)) for k in unit])
        solved = unit_values_sum == 45
    return solved

def main(display_units:bool=False):
    """Это основная функция для выполнения всех основных функций.
    Args:
        display_units (bool, optional): Возможность отображения единиц измерения. По умолчанию имеет значение Ложь.
    """
    
    if display_units:
        print(f"boxes : \n{boxes}\n")
        print(f"row_units : \n{row_units}\n")
        print(f"col_units : \n{col_units}\n")
        print(f"square_units : \n{square_units}\n")
        print(f"unit_lists : \n{unit_list}\n")
        
    # получить головоломку
    puzzle = get_puzzle()
    print("\nНерешенный Судоку.")
    display_sudoku(grid_values(puzzle,boxes,replace=False)) #показать оригинал
    
    print("\nСудоку с замененными точками на 1-9.")
    grid_units = grid_values(puzzle,boxes)
    display_sudoku(grid_units) #дисплей заменен
    
    print("\nСудоку с исключенными значениями.")
    eliminated_values=eliminate(grid_units)
    display_sudoku(eliminated_values) #дисплей устранен
    
    print("\nСудоку после замены только выбором.")
    elimination_with_only_coices_values=only_choice(eliminated_values)
    display_sudoku(elimination_with_only_coices_values)
    
    print("\nСудоку после распространения ограничения.")
    reduced_puzzle_values=reduce_puzzle(eliminated_values)
    display_sudoku(reduced_puzzle_values)
    
    solved = check_if_sudoku_solved(reduced_puzzle_values)
    if not solved:
        print("\nСудоку не решена и нуждается в поиске.")
        print("Судоку после поиска.")
        solved_puzzle_with_search=search(eliminated_values)
        display_sudoku(solved_puzzle_with_search)
        solved = check_if_sudoku_solved(solved_puzzle_with_search) 
        
    print(f'Судоку {"Решено" if solved else "Не решено"}.')
    
if __name__ == "__main__":
    
    main()