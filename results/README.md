# Preliminary Results

1. Managed to cause misclassification in:

      - activations, effect only during the attack

      - stored weights or instructions, the effect persisted after the attack until model reload

2. VGG-11 is more prone to produce inference errors during attack compared to ResNet-50

## Support

1. Shows an accuracy drop during the attack, and also cases with a permanent accuracy decrease after the attack. [[ResNet-50](exploratory/0002_spot/README.md)] [[ResNet-18](exploratory/0003_spot/README.md)] [[VGG-11](exploratory/0004_spot/README.md)]

1. Compares ResNet-50 and VGG-11 in attack with the same settings and location in VGG-11 resulted in more inference errors. (28 vs 45 in 128 samples) [[ResNet-50](exploratory/0002_spot/README.md)] [[VGG-11](exploratory/0004_spot/README.md)]

**Dataset** [link](https://www.kaggle.com/datasets/sautkin/imagenet1kvalid)
