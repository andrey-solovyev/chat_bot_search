import xlrd


class WorkWithFile:
    def __init__(self, name_of_file):
        self.name_of_file = name_of_file

    def search(self, textForSearch):
        theFile = xlrd.open_workbook(self.name_of_file)
        order = []
        for sheet in theFile.sheets():
            for rowidx in range(sheet.nrows):
                row = sheet.row(rowidx)
                array = []
                for colidx, cell in enumerate(row):
                    if textForSearch.lower() in str(cell.value).lower():
                        for coli, cells in enumerate(row):
                            array.append(str(cells.value))
                        order.append(array)
                        break
        return self.toString(order)

    def toString(self, orders):
        list = ""
        snowman = u'\U00002705'
        paragraph = u'\U000026AB'
        if len(orders) == 0:
            list += ("По вашему запросу ничего не найдено, пожалуйста проверьте корректность введенных данных")
        else:
            number = 1
            for n in orders:
                list += (snowman + "Товар №" + str(number) + "\n")
                list += ("Название товара: " + ' '.join(n[1].split()) + "\n")
                list += ("Артикуль: " + ' '.join(n[2].split()) + "\n")
                list += ("Производитель:" + ' '.join(n[3].split()) + "\n")
                list += ("Остаток:" + ' '.join(n[4].split()) + "\n")
                list += ("Опт: " + ' '.join(n[5].split()) + "\n")
                list += ("\n")
                number += 1
        return list
