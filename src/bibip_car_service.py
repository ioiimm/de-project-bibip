from datetime import datetime
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    def __get_item(self, file, line_number: int) -> list[str]:
        """Возвращает список параметров объекта из строки файла."""
        file.seek(line_number * (501))
        return file.read(500).strip().split(";")

    def __write_item(self, file, line_number: int, item: list[str]) -> None:
        """Записывает параметры объекта в строку файла."""
        file.seek(line_number * (501))
        file.write(';'.join(item).ljust(500))

    def __get_file_length(self, file) -> tuple[list[str], int]:
        """Возвращает список строк файла и количество этих строк."""
        data = file.readlines()
        return data, len(data)

    def __write_sorted(self, file, data: list) -> None:
        """Перезаписывает отсортированные строки в файл."""
        data.sort()
        file.seek(0)
        file.writelines(data)
        file.truncate()

    def __get_line_number(self, item: str) -> int:
        """Возвращает номер строки."""
        return int(item.strip().split(";")[-1])

    def __get_datetime(self, item: str) -> datetime:
        """Преобразует строку в объект datetime."""
        return datetime.strptime(item, "%Y-%m-%d %H:%M:%S")

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        # Формирование строки для записи в файл.
        new_model = str(model.id) + ";" + model.name + ";" + model.brand
        try:
            open('models_index.txt', 'r').close()
        except FileNotFoundError:
            open('models_index.txt', 'w').close()
        finally:
            # Запись строки с моделью в конец файла.
            with open("models.txt", "a") as f1:
                f1.write(new_model.ljust(500) + "\n")
            with open("models_index.txt", "r+") as f2:
                indexes, line_number = self.__get_file_length(f2)
                # Добавление, сортировка и запись индекса и номера строки.
                indexes.append(f"{model.id};{line_number}\n")
                indexes.sort(key=lambda x: int(x.split(";")[0]))
                f2.seek(0)
                f2.writelines(indexes)
                f2.truncate()
            return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        # Формирование строки для записи в файл.
        new_car = ";".join(map(str, [car.vin, car.model, car.price,
                                     car.date_start, car.status]))
        try:
            open('cars_index.txt', 'r').close()
        except FileNotFoundError:
            open('cars_index.txt', 'w').close()
        finally:
            # Запись строки с машиной в конец файла.
            with open("cars.txt", "a") as f1:
                f1.write(new_car.ljust(500) + "\n")
            with open("cars_index.txt", "r+") as f2:
                indexes, line_number = self.__get_file_length(f2)
                # Добавление, сортировка и запись индекса и номера строки.
                indexes.append(f"{car.vin};{line_number}\n")
                self.__write_sorted(f2, indexes)
            return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        # Формирование строки для записи в файл.
        new_sale = ";".join(map(str, [sale.sales_number, sale.car_vin,
                                      sale.sales_date, sale.cost]))
        try:
            open('sales_index.txt', 'r').close()
        except FileNotFoundError:
            open('sales_index.txt', 'w').close()
        finally:
            # Запись строки с продажей в конец файла.
            with open("sales.txt", "a") as f1:
                f1.write(new_sale.ljust(500) + "\n")
            with open("sales_index.txt", "r+") as f2:
                indexes, line_number = self.__get_file_length(f2)
                # Добавление, сортировка и запись индекса и номера строки.
                indexes.append(f"{sale.sales_number};{line_number}\n")
                self.__write_sorted(f2, indexes)
            # Обновление статуса машины.
            with open("cars_index.txt", "r") as f3:
                vin_indexes = f3.readlines()
                line_number = 0
                for i in vin_indexes:
                    if i.startswith(sale.car_vin):
                        line_number = self.__get_line_number(i)
                        break
            with open("cars.txt", "r+") as f4:
                updated_car = self.__get_item(f4, line_number)
                updated_car[-1] = "sold"
                self.__write_item(f4, line_number, updated_car)
            return Car(
                vin=updated_car[0],
                model=int(updated_car[1]),
                price=Decimal(updated_car[2]),
                date_start=self.__get_datetime(updated_car[3]),
                status=updated_car[4],
            )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        car_list = []
        with open("cars_index.txt", "r") as f1:
            line_number = self.__get_file_length(f1)[1]
        # Поиск машин с нужным статусом.
        with open("cars.txt", "r") as f2:
            for i in range(line_number):
                line = f2.read(501)
                car = line.strip().split(";")
                if car[-1] == status:
                    car_status = Car(
                        vin=car[0],
                        model=int(car[1]),
                        price=Decimal(car[2]),
                        date_start=self.__get_datetime(car[3]),
                        status=status,
                        )
                    car_list.append(car_status)
        return car_list

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        # Поиск номера строки.
        with open("cars_index.txt", "r") as f1:
            indexes = f1.readlines()
            line_number = 0
            existence = None  # Проверка наличия машины.
            for i in indexes:
                if i.startswith(vin):
                    line_number = self.__get_line_number(i)
                    existence = True
                    break
        # Если не удалось найти машину, возвращается None.
        if existence is None:
            return None
        # Собирается информация о машине и ее модели.
        with open("cars.txt", "r") as f2:
            car = self.__get_item(f2, line_number)
            model_id = car[1]
        with open("models_index.txt", "r") as f2:
            line_number = 0
            for i in f2.readlines():
                if i.split(";")[0] == model_id:
                    line_number = self.__get_line_number(i)
                    break
        with open("models.txt", "r") as f3:
            model = self.__get_item(f3, line_number)
        # Если машина не продана, возвращается информация без данных о продаже.
        if car[4] != "sold":
            car_info = CarFullInfo(
                vin=vin,
                car_model_name=model[1],
                car_model_brand=model[2],
                price=Decimal(car[2]),
                date_start=self.__get_datetime(car[3]),
                status=car[4],
                sales_date=None,
                sales_cost=None,
            )
            return car_info
        # Если машина продана, собираются данные о продаже.
        else:
            with open("sales.txt", "r") as f4:
                sales = f4.readlines()
                date_cost = ()
                for sale in sales:
                    sale_info = sale.strip().split(";")
                    if vin == sale_info[1]:
                        date_cost = sale_info[2], sale_info[3]
                        break
            car_info = CarFullInfo(
                vin=vin,
                car_model_name=model[1],
                car_model_brand=model[2],
                price=Decimal(car[2]),
                date_start=self.__get_datetime(car[3]),
                status=car[4],
                sales_date=self.__get_datetime(date_cost[0]),
                sales_cost=Decimal(date_cost[1]),
            )
            return car_info

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        with open("cars_index.txt", "r+") as f1:
            vin_indexes = f1.readlines()
            line_number = 0
            # Поиск номера строки по старому vin.
            # Замена старого vin на новый в файле "cars_index.txt".
            for i in range(len(vin_indexes)):
                if vin_indexes[i].startswith(vin):
                    line_number = self.__get_line_number(vin_indexes[i])
                    vin_indexes[i] = vin_indexes[i].replace(vin, new_vin)
                    break
            self.__write_sorted(f1, vin_indexes)
        # Обновление информации в файле "cars.txt".
        with open("cars.txt", "r+") as f2:
            car = self.__get_item(f2, line_number)
            car[0] = new_vin
            self.__write_item(f2, line_number, car)
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        with open("sales_index.txt", "r+") as f1:
            indexes = f1.readlines()
            line_number = 0
            # Поиск номера строки.
            # Добавление тега "canceled#" к индексу продажи.
            # Данные не удаляются, чтобы не перезаписывать
            # номера строк остальных продаж.
            for i in range(len(indexes)):
                if indexes[i].startswith(sales_number):
                    line_number = self.__get_line_number(indexes[i])
                    indexes[i] = indexes[i].replace(sales_number,
                                                    "canceled#" + sales_number)
                    break
            self.__write_sorted(f1, indexes)
        # Добавление тега "canceled#" к индексу продажи.
        with open("sales.txt", "r+") as f2:
            sale = self.__get_item(f2, line_number)
            sale[0] = "canceled#" + sale[0]
            vin = sale[1]
            self.__write_item(f2, line_number, sale)
        # Обновление статуса машины.
        with open("cars_index.txt", "r") as f3:
            vin_indexes = f3.readlines()
            for i in vin_indexes:
                if i.startswith(vin):
                    line_number = self.__get_line_number(i)
                    break
        with open("cars.txt", "r+") as f4:
            updated_car = self.__get_item(f4, line_number)
            updated_car[-1] = "available"
            self.__write_item(f4, line_number, updated_car)

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        with open("sales.txt", "r") as f1:
            # Собираются vin и стоимость проданных машин.
            sales = f1.readlines()
            vins = []
            costs = []
            for i in sales:
                if not i.startswith("canceled"):
                    sale = i.strip().split(";")
                    vins.append(sale[1])
                    costs.append(Decimal(sale[3]))
        # Определяются id моделей, количество продаж и общая стоимость.
        with open("cars_index.txt", "r") as f2:
            indexes = f2.readlines()
            for i in range(len(vins)):
                for j in indexes:
                    if j.startswith(str(vins[i])):
                        vins[i] = {vins[i]: self.__get_line_number(j)}
        with open("cars.txt", "r") as f3:
            models = {}
            for i in range(len(vins)):
                for value in vins[i].values():
                    car = self.__get_item(f3, value)
                    model_id = car[1]
                    try:
                        models[model_id][0] += 1
                        models[model_id][1] += costs[i]
                    except KeyError:
                        models[model_id] = [1, costs[i]]
        # Словарь с id моделей ранжируется по количеству продаж и
        # общей стоимости.
        # Выделяется топ-3.
        top_models = sorted(models.items(),
                            key=lambda x: (-x[1][0], -x[1][1]))[:3]
        # По id находятся данные о названии моделей и бренда.
        # Формируется список с объектами класса ModelSaleStats.
        stats = []
        with open("models_index.txt", "r") as f4:
            indexes = f4.readlines()
            for i in range(3):
                for j in indexes:
                    line = j.strip().split(";")
                    if line[0] == top_models[i][0]:
                        top_models[i][1][1] = int(line[1])
        with open("models.txt", "r") as f5:
            for i in top_models:
                model = self.__get_item(f5, i[1][1])
                stats.append(ModelSaleStats(
                    car_model_name=model[1],
                    brand=model[2],
                    sales_number=i[1][0],
                ))
        return stats
