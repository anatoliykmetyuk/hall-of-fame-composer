import dotenv, os, yaml, re

from langchain.document_loaders.googledrive import GoogleDriveLoader
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from pydantic import BaseModel, Field

dotenv.load_dotenv()

SCALACENTER_SHEETS_ID = os.getenv("SCALACENTER_SHEETS_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")
PROJECT_HOME = os.getenv("PROJECT_HOME")
OUT_PATH = os.getenv("OUT_PATH")
out_file = os.path.join(OUT_PATH, 'gs_projects.yaml')

# Load the docs
def load_docs():
  loader = GoogleDriveLoader(folder_id=SCALACENTER_SHEETS_ID)
  return loader.load()

# Define the domain model
class Project(BaseModel):
    name: str = Field(description="name of the project")
    web: str | None = Field(description="url of the project homepage")
    github: str | None = Field(description="url of the github repository")
    origin: str | None = Field(description="url of the advisory board proposal that initiated the project")
    contributors: list = Field(description="list of contributors")
    process: bool = Field(description="true if it's an organisational process, "+
                          "false if it's a technical project")
    category: str = Field(description="category of the project, one of: "+
                          '"compiler", "library", "tooling", "documentation", "process"')
    description: str = Field(description="description of the project")
    start_year: int | None = Field(description="year the project started")
    end_year: int | None = Field(description="year the project ended")
parser = PydanticOutputParser(pydantic_object=Project)

# Create the template
def create_chain():
  template = PromptTemplate(
      template='''
        Given a project description, extract data as per the following format:
        {format_instructions}

        Considerations:
        - `category` MUST be present at all times. Do your best to categorize
          to one of the categories specified by the format above.

        The project data is provided between the backticks below:
        ```
        {project_data}
        ```
      ''',
      input_variables=['project_data'],
      partial_variables={
        'format_instructions': parser.get_format_instructions(),
      }
  )

  # Create the model
  llm = ChatOpenAI(openai_api_key=OPENAI_KEY, model='gpt-3.5-turbo')
  return LLMChain(llm=llm, prompt=template, output_parser=parser)

def refine(parsed: dict):
  if not parsed['origin']:
    return parsed
  match = re.match(r'SCP-(\d+)', parsed['origin'])
  if match:
    scp_number = int(match.group(1))
    with open(os.path.join(PROJECT_HOME, 'data', 'ab_proposals.txt')) as f:
      lines = f.readlines()
    file_name = lines[scp_number-1].strip()
    url = f'https://github.com/scalacenter/advisoryboard/blob/main/proposals/{file_name}'
    parsed['origin'] = url
  else:
    parsed['origin'] = None
  return parsed

def process_docs(docs, chain, output_file):
  results = []
  for i, doc in enumerate(docs):
    print(f'Processing doc {i+1} / {len(docs)}')
    res = chain.predict(project_data=doc.page_content).model_dump()
    res = refine(res)
    results.append(res)
  with open(output_file, 'w') as f:
    yaml.dump(results, f, sort_keys=False)

if __name__ == '__main__':
  docs = load_docs()
  chain = create_chain()
  process_docs(docs[:5], chain, out_file)
