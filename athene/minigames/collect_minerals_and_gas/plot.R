# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

# To draw a plot use:
# $ Rscript plot.R

results <- read.csv("../../memory/collect_minerals_and_gas/score.csv")

plot(
    results$score,
    main="Collect minerals and gas",
    xlab="Episodes",
    ylab="Score",
    col="blue",
    type="l"
)

