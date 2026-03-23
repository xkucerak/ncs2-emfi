# Preliminary Results

1. Managed to cause misclassification in:

      - activations, effect only during the attack

      - stored weights or instructions, the effect persisted after the attack until model reload

2. VGG-11 is more prone to produce inference errors during attack compared to ResNet-50

## Support

1. Shows an accuracy drop during the attack, and also cases with a permanent accuracy decrease after the attack.

   |                    model                     |                TOP 1 ACC                |
   | :------------------------------------------: | :-------------------------------------: |
   | [ResNet-18](exploratory/0003_spot/README.md) | ![alt](exploratory/0003_spot/top_1.svg) |
   | [ResNet-50](exploratory/0002_spot/README.md) | ![alt](exploratory/0002_spot/top_1.svg) |
   |  [VGG-11](exploratory/0004_spot/README.md)   | ![alt](exploratory/0004_spot/top_1.svg) |

1. Comparing ResNet-50 and VGG-11 in an attack with the same settings and location. The VGG-11 model resulted in more inference errors (28 vs 45 in 128 samples). And VGG-11 shows better resistance against the attack, by maintaining some accuracy.
   | model | TOP 1 ACC |
   | :------------------------------------------: | :-------------------------------------: |
   | [ResNet-50](exploratory/0002_spot/README.md) | ![alt](exploratory/0002_spot/top_1.svg) |
   | [VGG-11](exploratory/0004_spot/README.md) | ![alt](exploratory/0004_spot/top_1.svg) |

**Dataset** [link](https://www.kaggle.com/datasets/sautkin/imagenet1kvalid)
