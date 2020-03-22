class Gap_Trader(QCAlgorithm):
    # Initialization to 2/19 values

    def Initialize(self):
        self.setConstants()
        self.SetStartDate(2007, 12, 1)  # Set Start Date
        self.SetEndDate(2009, 5 , 20)
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
        #self.Debug(str(bar.EndTime - bar.Time) + " " + bar.ToString())
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
        if data.Bars.ContainsKey("SPY"):
            self.spy_curr = data["SPY"].Price
        if data.Bars.ContainsKey("SPXL"):
            self.spxl_curr = data["SPXL"].Price
        if data.Bars.ContainsKey("SPXS"):
            self.spxs_curr = data["SPXS"].Price
        #self.Consolidate("SPY", timedelta(minutes=5), self.fiveMinuteConsolidator)
        #print("SPY 5 minute bar at: {0}".format(self.fiveMinuteConsolidator.Price))
        return;


    def MarketOpen(self):
        close = self.spy_close
        #open = self.Securities["SPY"].Price
        open = self.spy_curr
        #self.Log("close price: {0}".format(close))
        #self.Log("open price: {0}".format(open))
        # Gap Up
        if (close < open):
            shares = self.find_shares(close, open, self.spxs_curr)
            self.Log("Gap Up: Buy {0} SPXS Shares".format(shares))
            self.MarketOrder("SPXS", shares)
        # Gap Down
        else:
            shares = self.find_shares(close, open, self.spxl_curr)
            self.Log("Gap Down: Buy {0} SPXL Shares".format(shares))
            self.MarketOrder("SPXL", shares)
        return

    def MarketClose(self):
        # Liquidate all holdings at market close
        self.Liquidate()

        # Update Market Close prices
        self.spxl_close = self.Securities["SPXL"].Price
        self.spxs_close = self.Securities["SPXS"].Price
        self.spy_close = self.Securities["SPY"].Price
        return

    def setConstants(self):
        self.granularity = 4
        self.multiplier = 10
        self.spxl_close = 75.83
        self.spxs_close = 11.37
        self.spy_close =  338.34
        self.spxl_curr = 75.83
        self.spxs_curr = 11.37
        self.spy_curr =  338.34
        return

    def OnEndOfAlgorithm(self):
        return;
