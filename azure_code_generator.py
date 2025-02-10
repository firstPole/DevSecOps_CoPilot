from openai import AzureOpenAI
import aiohttp
def generate_code_from_azure(endpoint, api_key, prompt, api_version, deployment_name):
    """
    Sends a request to Azure OpenAI's gpt-4o-mini model to generate YAML.

    Args:
        endpoint: Azure OpenAI endpoint URL.
        api_key: Your Azure OpenAI API key.
        prompt: Additional information to guide the code generation.
        api_version: API version supported by your model deployment (check Azure OpenAI documentation).
        deployment_name: The exact deployment name of your gpt-4o-mini model in Azure OpenAI.

    Returns:
        The generated YAML code as a string.
    """

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )

    response = client.chat.completions.create(
        model=deployment_name,
         messages=[
        {
            "role": "system",
            "content": (
               "You are an expert in generating clean, modular, scalable, and reusable code. "
                "The code should follow best practices for software architecture, focusing on high maintainability and easy scalability. "
                "Please organize the code into functions, classes, or modules as appropriate to make it easy to reuse in different contexts. "
                "Ensure the code is well-commented and follows the principles of SOLID design patterns, aiming for simplicity and clarity. "
                "Additionally, ensure that security and performance considerations are addressed while maintaining modularity and reusability. "
                "Where applicable, provide meaningful variable names, and break down complex logic into smaller, easier-to-understand components."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{prompt}\n\n"
                "The output must be syntactically correct, correctly indented, and formatted as per the type of generated output."
                "In addition to generating the code, also provide a list of all placeholders, variables, "
                "and values that need to be replaced, along with a brief description of each. Ensure the list is at the bottom of the generated output."
            ),
        },
    ],
    max_tokens=5000,
    temperature=0.7,  # Adjust temperature for creativity vs. accuracy
    top_p=1,
    n=1,
    stop=None,
)

    generated_code = response.choices[0].message.content 
    return generated_code

async def generate_code_from_azure_async(endpoint, api_key, prompt, api_version, deployment_name):
  """
  Sends a request to Azure OpenAI's GPT-4o-mini model to generate YAML asynchronously.

  Args:
      endpoint: Azure OpenAI endpoint URL.
      api_key: Your Azure OpenAI API key (**verify correctness**).
      prompt: Additional information to guide the code generation.
      api_version: API version supported by your model deployment (check Azure OpenAI documentation).
      deployment_name: The exact deployment name of your GPT-4o-mini model in Azure OpenAI (**match exactly**).

  Returns:
      The generated code as a string, or an error message if the request fails.
  """
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
  }

  # Prepare the data to send to the model
  data = {
      "model": deployment_name,
      "messages": [
          {"role": "system", "content":
              "You are an expert in generating CI/CD pipelines and DevOps automation code. "
              "You should strive to produce high-quality, secure, and well-structured code. "
              "Pay close attention to best practices and security considerations. "
              "Consider incorporating features like vulnerability scanning, service mesh integration, and configuration management."
          },
          {"role": "user", "content": prompt}
      ],
      "max_tokens": 5000,
      "temperature": 0.7,  # Adjust temperature for creativity vs. accuracy
      "top_p": 1,
      "n": 1,
      "stop": None
  }

  # Construct the complete URL with endpoint, deployment, and API version
  url = f"{endpoint}/openai/deployments/{deployment_name}/completions?api-version={api_version}"

  async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, json=data) as response:
          if response.status == 200:
              response_json = await response.json()
              # Extract the generated code from the response
              generated_code = response_json["choices"][0]["message"]["content"]
              return generated_code
          else:
              # If there is an error, print the error message and status code
              print(f"Error: HTTP {response.status} - {await response.text()}")
              return f"Error: HTTP {response.status}"