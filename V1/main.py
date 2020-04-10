class Gap_Trader(QCAlgorithm):
    # Initialization to 2/19 values

    def Initialize(self):
        self.setConstants()
        self.SetStartDate(2020, 2, 20)  # Set Start Date
        self.SetEndDate(2020, 3 , 20)
        self.SetCash(50000)  # Set Strategy Cash
        self.spxl = self.AddEquity("SPXL", Resolution.Minute, Market.USA, True, 1, True).Symbol
        self.spxs = self.AddEquity("SPXS", Resolution.Minute, Market.USA, True, 1, True).Symbol
        self.spy = self.AddEquity("SPY", Resolution.Minute, Market.USA, True, 1, True).Symbol
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.AfterMarketOpen("SPY", 0), Action(self.MarketOpen))
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.BeforeMarketClose("SPY", 1), Action(self.MarketClose))
        self.SetWarmUp(timedelta(20))
        self.consolidateBars();

    def consolidateBars(self):
        self.spy_consolidator = TradeBarConsolidator(timedelta(minutes=self.granularity))
        self.spy_consolidator.DataConsolidated += self.Consolidate_Handler
        self.SubscriptionManager.AddConsolidator("SPY", self.spy_consolidator)

    def Consolidate_Handler(self, sender, bar):
        self.Log(bar.Price)
        if (self.Securities["SPXL"].Holdings.HoldStock and bar.Close < bar.Open):
            self.Liquidate();
        elif (self.Securities["SPXS"].Holdings.HoldStock and bar.Close > bar.Open):
            self.Liquidate();
        return

    def find_gap(self, price1, price2):
        return abs((price1-price2)/price1)

    def find_shares(self, close, open, asset):
        gap = self.find_gap(close, open)
        capital = self.Portfolio.Cash
        return round(gap*capital*self.multiplier/asset)

    def SpecificTime(self):
        self.Log("SpecificTime: Fired at : {0}".format(self.Time))
        return

    def OnData(self, data):
        return;


    def MarketOpen(self):
        # Gap Up
        close = self.close
        open = self.Securities["SPY"].Price
        if (close < open):
            shares = self.find_shares(close, open, self.Securities["SPXS"].Price)
            self.Log("Gap Up: Buy {0} SPXS Shares".format(shares))
            self.MarketOrder("SPXS", shares)
        # Gap Down
        else:
            shares = self.find_shares(close, open, self.Securities["SPXL"].Price)
            self.Log("Gap Down: Buy {0} SPXL Shares".format(shares))
            self.MarketOrder("SPXL", shares)
        return

    def MarketClose(self):
        # Liquidate all holdings at market close
        self.close = self.Securities["SPY"].Price
        self.Liquidate()
        return

    def setConstants(self):
        self.granularity = 4
        self.multiplier = 10
        self.close = 338.34
        return

    def OnEndOfAlgorithm(self):
        return;
