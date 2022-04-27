        
        return self.__dict__
    
runners = ["4892470", "5830181", "6178", "257551", "3476381", "7473221"]

for runner in runners:

    runner = Runner.scrape(runner=runner)
    display(runner.json())

        
for mid in ["1Om06X9TE4AA4NI4r79yADnjMp90", "1ImV8WgyJK51NLiTeZUC17IlnA4I"]:
    
    display(Map.scrape(mid=mid).json())