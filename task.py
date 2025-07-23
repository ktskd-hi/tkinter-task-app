from pydantic import BaseModel, ConfigDict
from dataclasses import dataclass
from typing import List

class Category(BaseModel):
    id: int
    title: str
    color: str

@dataclass
class CategoryList:
    categories: List[Category]

class Task(BaseModel):
    # model_config = ConfigDict()
    id: int
    title: str = "タイトル未設定"
    priority: int = 1
    estimatedCost: float = 1.0
    status: str = "未着手"
    check: bool
    category: Category
    displayOrder: int
    about: str = None

@dataclass
class TaskList:
    tasks: List[Task]

    def calcCostSum(
        self,
        selected_sort_id: int,
        selected_filter_status_list: List[bool],
        filter_status_name_list: List[str]
    ) -> List[float]:
        self.costSumList = []
        if selected_sort_id == 2:
            sortedTasks = sorted(self.tasks, key=lambda task: task.category.id)
        elif selected_sort_id == 3:
            sortedTasks = sorted(self.tasks, key=lambda task: task.priority, reverse=True)
        elif selected_sort_id == 4:
            sortedTasks = sorted(self.tasks, key=lambda task: task.estimatedCost, reverse=True)
        else:
            sortedTasks = sorted(self.tasks, key=lambda task: task.displayOrder)



        dispStatusList = []
        noDispStatusList = []
        dispOthers = False

        for i, boolean in enumerate(selected_filter_status_list):
            if boolean == True:
                addName = filter_status_name_list[i]
                if addName == "その他":
                    dispOthers = True
                else:
                    dispStatusList.append(addName)
            else:
                addName = filter_status_name_list[i]
                if addName != "その他":
                    noDispStatusList.append(addName)


        for i, task in enumerate(sortedTasks):
            costSum = 0
            if dispOthers:
                for j in range(i+1):
                    if sortedTasks[j].check and sortedTasks[j].status not in noDispStatusList and sortedTasks[j].displayOrder != 9999:
                        costSum += sortedTasks[j].estimatedCost
                if sortedTasks[i].status not in noDispStatusList and sortedTasks[i].displayOrder != 9999:
                    self.costSumList.append(costSum)

            else:
                for j in range(i+1):
                    if sortedTasks[j].check and sortedTasks[j].status in dispStatusList and sortedTasks[j].displayOrder != 9999:
                        costSum += sortedTasks[j].estimatedCost
                if sortedTasks[i].status in dispStatusList and sortedTasks[i].displayOrder != 9999:
                    self.costSumList.append(costSum)
        return self.costSumList
    
    def getSortedTaskList(self, selected_sort_id: int):
        if selected_sort_id == 2:
            sortedTasks = sorted(self.tasks, key=lambda task: task.category.id)
        elif selected_sort_id == 3:
            sortedTasks = sorted(self.tasks, key=lambda task: task.priority, reverse=True)
        elif selected_sort_id == 4:
            sortedTasks = sorted(self.tasks, key=lambda task: task.estimatedCost, reverse=True)
        else:
            sortedTasks = sorted(self.tasks, key=lambda task: task.displayOrder)

        return sortedTasks




class GoalLine(BaseModel):
    id: int
    title: str
    cost: float
    memo: str
    color_id: int
    graphDisp: bool
    categorySize: List[float]


@dataclass
class GoalLineList:
    goallines: List[GoalLine]

    def replace_at_same_position(self, new_goalline: GoalLine):
        for i, goalline in enumerate(self.goallines):
            if goalline.id == new_goalline.id:
                self.goallines[i] = new_goalline
                return True
        return False
    
    def add(self, goalline: GoalLine):
        self.goallines.append(goalline)
