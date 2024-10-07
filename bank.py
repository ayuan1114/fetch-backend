import pandas as pd

class PointBank:
    def __init__(self):
        self.transactions = pd.DataFrame(columns = ['payer', 'points', 'timestamp'])
    
    # helper function for add that bsearches timestamp location and inserts the new transaction
    def insert(self, payer: str, points: int, timestamp: str):
        mini = -1
        maxi = len(self.transactions)
        while (maxi - mini > 1):
            cur = (maxi + mini) // 2
            if self.transactions.iloc[cur]['timestamp'] >= timestamp:
                maxi = cur
            else:
                mini = cur
        if maxi == len(self.transactions.index):
            self.transactions.loc[len(self.transactions.index)] = [payer, points, timestamp]
        elif self.transactions.iloc[0]['timestamp'] > timestamp:
            self.transactions = pd.concat([pd.DataFrame([{'payer': payer, 'points': points, 'timestamp': timestamp}]), self.transactions], ignore_index=True)
        else:
            df1 = self.transactions[0:maxi]
            df2 = self.transactions[maxi:]
            df1.loc[maxi] = [payer, points, timestamp]
            self.transactions = pd.concat([df1, df2])
        self.transactions.index = [*range(self.transactions.shape[0])]
        

    def add(self, payer: str, points: int, timestamp: str):
        if points < 0:
            allIn = self.transactions[(self.transactions['payer'] == payer) & (self.transactions['timestamp'] <= timestamp)]['points']
            if sum(allIn) + points >= 0:
                allIn = allIn.index
                cur = len(allIn) - 1
                while points < 0:
                    if points + self.transactions.iloc[allIn[cur]]['points'] > 0:
                        self.transactions.at[allIn[cur], 'points'] += points
                        break
                    else:
                        points += self.transactions.iloc[allIn[cur]]['points']
                        self.transactions.at[allIn[cur], 'points'] = 0
                        if points == 0:
                            break
                    cur -= 1
                self.transactions = self.transactions[self.transactions['points'] != 0]
                self.transactions.index = [*range(self.transactions.shape[0])]
            else:
                return -1
        else:
            self.insert(payer, points, timestamp)
    
    def balance(self):
        return self.transactions.groupby(by=['payer'])['points'].sum()

    def spend(self, points: int):
        if sum(self.transactions['points']) + points < 0:
            return -1
        payers = {}
        curInd = 0
        while True:
            if self.transactions.iloc[curInd]['points'] > points:
                self.transactions.at[curInd, 'points'] -= points
                if self.transactions.iloc[curInd]['payer'] in payers.keys():
                    payers[self.transactions.iloc[curInd]['payer']] -= points
                else:
                    payers[self.transactions.iloc[curInd]['payer']] = -points
                break
            else:
                points -= self.transactions.iloc[curInd]['points']
                if self.transactions.iloc[curInd]['payer'] in payers.keys():
                    payers[self.transactions.iloc[curInd]['payer']] -= self.transactions.iloc[curInd]['points']
                else:
                    payers[self.transactions.iloc[curInd]['payer']] = -self.transactions.iloc[curInd]['points']
            curInd += 1
            if points == 0:
                    break
        self.transactions = self.transactions[curInd:]
        return payers