from flask import Flask, jsonify, request, abort
from poke_api_wrapper import PokeAPI

app = Flask(__name__)
poke_api = PokeAPI()

# Armazenamento de times (pode ser substituído por BD)
times = {}

@app.route("/api/teams", methods=["GET"])
def listar_times():
  """Lista todos os times registrados."""
  return jsonify(list(times.values()))

@app.route("/api/teams/<string:user>", methods=["GET"])
def buscar_time(user):
  """Busca um time pelo nome do usuário."""
  if user not in times:
    abort(404, description="Time não encontrado")
  return jsonify(times[user])

@app.route("/api/teams", methods=["POST"])
def criar_time():
  """Cria um novo time."""
  if not request.json:
    abort(400, description="JSON inválido")

  try:
    nome_usuario = request.json["nomeUsuario"]
    pokemons = request.json["pokemons"]
    validar_pokemons(pokemons)

    # Criar novo time e adicionar à lista
    times[nome_usuario] = {
      "nomeUsuario": nome_usuario,
      "pokemons": obter_detalhes_pokemons(pokemons)
    }

    return jsonify({"mensagem": "Time criado com sucesso!"}), 201

  except KeyError:
    abort(400, description="Chave ausente no JSON")
  except PokemonNaoEncontrado as e:
    abort(400, description=str(e))

def validar_pokemons(pokemons):
  """Verifica se todos os Pokémons existem na PokéAPI."""
  for pokemon in pokemons:
    if not poke_api.get_pokemon_by_name(pokemon):
      raise PokemonNaoEncontrado(pokemon)

def obter_detalhes_pokemons(pokemons):
  """Obtém detalhes dos Pokémons da PokéAPI."""
  return [
    {
      "idPokedex": pokemon.id,
      "nome": pokemon.name,
      "altura": pokemon.height / 10, # converter para decimetros
      "peso": pokemon.weight / 10 # converter para hectograms
    } for pokemon in poke_api.get_pokemons_by_names(pokemons)
  ]

class PokemonNaoEncontrado(Exception):
  """Exceção para Pokémon não encontrado na PokéAPI."""
  def __init__(self, pokemon):
    self.pokemon = pokemon
  
  def __str__(self):
    return f"Pokémon '{self.pokemon}' não encontrado na PokéAPI."

if __name__ == "__main__":
  app.run(debug=True)
