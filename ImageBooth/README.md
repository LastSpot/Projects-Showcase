# Team 30 Project

Project name: ImageBooth

## Updates
* ADD front-end validator and back-validator
* replace the simple search function with power fuzzy Search, user now can search by tags, description, and name at same time, just like whaat they use the Google search engine!


We do the task1 server-like function part outstand the standard by actually create a js server and do most api we need with PouchDb.
I claim we also outstand by:
1. follow ES6 structure using package.json, easy for developers to setup their env
2. fulfill the task3 data mock part, we create mock data and a script that allows any developer to easily generate 1000 records of user login and models into database so we don't copy the same database between developers.

however, we realized we didn't make everything expecially the render prefect since we found its hard for us to work for the render part without finished the design and framework of all api since our APP is a search engine like webpage which heavy dependents on api interaction (and it's not possible to render only with one or two data in hand so we also need to finished the data mock part first)

We just spent too much time doing the "outstanding" part of task1, I believe if we have more time, we will do better on task2.

Thx for you understanding

## Team Overview

- JIARUI LIU @Catkamakura
<!-- - Changhyo Shon @changhyoshon100 -->
- Minh Le @LastSpot
<!-- - Kaitlyn Nguyen @kaitlynnguye -->

## Innovative Idea

Our project aims to create a collection library and search engine for not only prompts but also publicly available fine-tune models like Dreambooth and custom diffusion, which we believe will make a beginner AI image generator user's life easier. The application will have a search functionality with matching that allow users to retrieve images in our collection that match their text description. Our aim is help user generate images that better fit the description.

### Background and related work

With the rise of deep neural networks, AI image generation grows more explosively this year with the rise of deep neural networks and the development of advanced deep learning models like stable diffusion. Merely with a short input sentence of prompt, recent models are capable of generating stunningly realistic and complex images that are often indistinguishable from those created by humans. AI image generation has completely revolutionized the way we think about creating images. Now average people are able to create their work like a pro with the help of AI.

How to generate an image you want with a text-to-image model like stable diffusion? Well, you just need to construct a description of what you want. For example, "a dog with sunglass near the beach". Boom, after seconds of waiting, the image is ready for you.

However, it's not easy to describe every detail about a picture in a machine-understandable way using natural language, so the majority of users prefer a list of tokens to choose as the prompt for a better output. While prompts like "supercalifragilisticexpialidocious-ly" work, they are not "human-friendly", especially for those newcomers. A masterpiece AI-generated image often needs an overlong and miscellaneous token list. Here's an example of a prompt:

> "masterpiece, best quality, ultra-detailed, illustration, solo, dynamic angle, floating, beautiful detailed sky, detailed water, expressionless, ribbons, bowties, buttons, flowers."

A prompt cookbook & search engines like arthub.ai and lexica.art are necessary for beginners. They collect various AI-generated works and corresponding prompts to help the user construct their prompt. The user could search for some keywords or simple descriptions of their ideas and get inspiration from similar works on the website.

### Intro of our project

AI image generation becomes more friendly as fine-tuning models like DreamBooth and custom Diffusion, which both came out not too long ago. Those models allow the user to "personalize" text-to-image diffusion models with just a few images of a subject and generate high-quality results with short descriptions/prompts. Users then have no need to worry about prompt chants.

But at the same time, given there's a script and package that allows people to train their own finetuned model without a line of code, training the "personal" model is still hard for the masses. Most people are idle about collecting proper input materials and playing with the model UI. They would rather just grab and use the relevant trained fine-tune model from others. Some authors share their finetuned models on concept library like https://huggingface.co/sd-dreambooth-library, but more are shared in a small range via discord/telegram server(though those models are under CC-BY-NC 4.0 license). There is a need for an open collection and search engine for those finetuned models!

## Data

- User data: username, email for Authentication; search history for ranking algorithm and data analysis
- Prompts of selected AI-generated image: prompt with the image, as it is on arthub.ai
- Publicly available fine-tuned models(or URL of them) of DreamBooth, custom Diffusion, and etc.: short description or keywords for the models, and the model resource(URL or file itself)
- Log: log for developer debug use and data analysis

## Functionality

### Stable Diffusion tokenizer

The tokenizer could tokenize descriptions in natural language into a list of tag Diffusion used in image generation, which allows the user to search prompts and models in natural language.

### Search engine

Allows the user to search prompts and models related to his interests. May support fuzzy matching to improve user experience.
The user types a short text of what he wants to generate and our website tokenizer will first transform it into a list of tags(tokens). Then the search engine will search for related works in our database and return them to the user.

### Add resource

We would allow verified users to add resources(prompts, models) to our database.

### Ranking

Using users' search history, we may show the most popular tags by some ranking algorithm.

### crawler

We may use a web crawler to keep our resources up-to-date.

## License

[MIT License](https://opensource.org/licenses/MIT)
