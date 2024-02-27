library(tidyverse)
library(lme4)
library(modelr)
library(lmtest)
library(car)
library(viridis)
library(ggrepel)
library(latex2exp)
library(argparse)

# create parser object
parser <- ArgumentParser()

parser$add_argument(
  "data_fn",
  nargs=1, 
  help="Path to CSV file containing language measurements."
)

parser$add_argument(
  "save_dir",
  nargs=1,
  help="Path to directory to save plots."
)

args <- parser$parse_args()


df_fn <- args$data_fn
save_dir <- args$save_dir

# Load data
df <- read_csv(df_fn)

# Make an alias, facet_var, for original name
df <- mutate(df, facet_var = paste(original_name, "and variants"))

pareto_data <- filter(df, dominant == TRUE)
natural_data <- filter(df, natural == TRUE)
variants_data <- filter(df, str_detect(name, "_variant_"))
naturals_and_variants_df <- bind_rows(natural_data, variants_data)


(
  # Set data and the axes
  ggplot(
    mapping=aes(x=complexity, y=comm_cost),
  )
  # + scale_y_continuous(limits=[0, 1])
  + geom_line(
    # remove faceting variable here so it is present in facet_wrap
    data=select(pareto_data, -facet_var),
  )
  + geom_point(  # all langs
      data=naturals_and_variants_df,
      stroke=0,
      alpha=.5,
      mapping=aes(
        # color=original_name,
        color=dp_medium,
        shape=dp_medium,
      ),
      size=3,
  )
  + geom_point( # natural langs
    data=natural_data,
    shape="+",
    size=8,
  )
  # Annotate originals
  + geom_text_repel(
    data=natural_data,
    mapping=aes(label=name),
    size=4,
    nudge_x=2,
  )  
  
  + facet_wrap(vars(facet_var))
  
  + scale_color_discrete()
  # + theme_classic()
)
save_fn <- paste(save_dir, "/", "faceted_langs", ".png", sep="")
ggsave(
  save_fn,
  width=10,
  height=10,
)

# Regressions
df_s <- df %>% 
  mutate(
    optimality_z = scale(optimality),
)

# Predict (unscaled for now, so range [0,1]) optimality from
# - natural (bool)
# - dp_medium (bool)
# - no interaction, because no case where natural=1 and dp=0

model0 <- lm(optimality ~ natural + dp_medium, df_s)
summary_output <- capture.output(summary(model0))
save_fn <- paste(save_dir, "/", "model_summary_0", ".txt", sep="")
writeLines(summary_output, save_fn)

model1 <- lmer(optimality ~ natural + dp_medium + (1 | original_name), df_s)
summary_output <- capture.output(summary(model1))
anova_output <- capture.output(Anova(model1))
writeLines(summary_output, paste(save_dir, "/", "model_summary_1", ".txt", sep=""))
writeLines(anova_output, paste(save_dir, "/", "model_anova_1", ".txt", sep=""))


# Likelihood Ratio Tests

#fit full model
model_full <- lmer(optimality ~ natural + dp_medium + (1 | original_name), data = df_s)

#fit reduced models
model_natural <- lmer(optimality ~ natural + (1 | original_name), data = df_s)
model_dp <- lmer(optimality ~ dp_medium + (1 | original_name), data = df_s)

#perform likelihood ratio test for differences in models
lr_dp <- lrtest(model_full, model_natural)
lr_natural <- lrtest(model_full, model_dp)

summary_output <- capture.output(summary(lr_dp))
writeLines(summary_output, paste(save_dir, "/", "likelihood_ratio_without_dp", ".txt", sep=""))

summary_output <- capture.output(summary(lr_natural))
writeLines(summary_output, paste(save_dir, "/", "likelihood_ratio_without_natural", ".txt", sep=""))
