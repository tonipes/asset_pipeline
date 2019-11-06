# Asset Builder

Tool for automated asset pipeline

## Configuration

Asset actions are defined in a configuration file

### Configuration variables

- relative_folder

- relative_filepath

- input_filepath

- output_filepath

- input_local_folder

- output_local_folder

- input_root_folder

- output_root_folder


### Example configuration

```json
{
  "actions": [{
    "type": "copy",
    "desc": "Copy action",
    "globs": [
      "**.txt",
      "**.mp3",
    ]
  },{
    "type": "copy",
    "desc": "Another copy action",
    "globs": [
      "**.wav"
    ]
  },{
    "type": "external",
    "desc": "Example external action",
    "command": [
      "some_program", "-i", "{input_filepath}", "-o", "{output_filepath}", "--option", "yes",
    ],
    "globs": [
      "**.somefile"
    ]
  }]
}

```
