suppressPackageStartupMessages(library(multcompView))
# I need to group the treatments that are not different each other together.
generate_label_df <- function(TUKEY, variable){
 
     # Extract labels and factor levels from Tukey post-hoc 
     Tukey.levels <- TUKEY[[variable]][,4]
     Tukey.labels <- data.frame(multcompLetters(Tukey.levels)['Letters'])
     
     #I need to put the labels in the same order as in the boxplot :
     Tukey.labels$treatment=rownames(Tukey.labels)
     Tukey.labels=Tukey.labels[order(Tukey.labels$treatment) , ]
     return(Tukey.labels)
     }
 
boxplot_tukey <- function(data, filename){
    
    # What is the effect of the treatment on the value ?
    model=lm( data$value ~ data$treatment )
    ANOVA=aov(model)
     
    # Tukey test to study each pair of treatment :
    TUKEY <- TukeyHSD(x=ANOVA, 'data$treatment', conf.level=0.95)
     
    pdf(filename)
    # Tuckey test representation :
    #plot(TUKEY , las=1 , col="brown")
    
    # Apply the function on my dataset
    LABELS <- generate_label_df(TUKEY , "data$treatment")
     
    # A panel of colors to draw each group with the same color :
    my_colors <- c( 
      rgb(143,199,74,maxColorValue = 255),
      rgb(242,104,34,maxColorValue = 255), 
      rgb(111,145,202,maxColorValue = 255)
      )
     
    # Draw the basic boxplot
    a <- boxplot(data$value ~ data$treatment , ylim=c(min(data$value) , 1.1*max(data$value)) , col=my_colors[as.numeric(LABELS[,1])] , ylab="value" , main="")
     
    # I want to write the letter over each box. Over is how high I want to write it.
    over <- 0.1*max( a$stats[nrow(a$stats),] )
     
    #Add the labels
    text( c(1:nlevels(data$treatment)) , a$stats[nrow(a$stats),]+over , LABELS[,1]  , col=my_colors[as.numeric(LABELS[,1])] )
    dev.off()
}
if (!interactive()) {
    args <- commandArgs(trailingOnly = TRUE)
    data <- read.delim(args[1]) 
    filename <- args[2] 
    boxplot_tukey(data, filename)
    file.remove(args[1])
    #print(args)
}


