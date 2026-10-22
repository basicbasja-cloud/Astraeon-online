/* Generated from factory-v3/patch-0.0.1/factory.json; policy is not art approval. */
(function(scope){'use strict';
const freeze=o=>{if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o)}return o};
const policy=freeze({
  "patch": "0.0.1",
  "anatomy": {
    "frameWidth": 240,
    "frameHeight": 240,
    "rootAnchorX": 120,
    "rootAnchorY": 172,
    "referenceHeight": 88
  },
  "classes": {
    "0": {
      "id": "swordsman",
      "name": "Swordsman",
      "archetype": "warrior",
      "clips": [
        "Walk",
        "Run",
        "Sprint",
        "Hit",
        "Death",
        "Interact",
        "Pickup",
        "ItemUse",
        "Sit",
        "Respawn",
        "Idle",
        "CombatIdle",
        "BasicAttack",
        "SkillAction",
        "CastChannel",
        "CastRelease",
        "Guard",
        "Dash",
        "SpinAttack"
      ],
      "combatBindings": {
        "attack": "BasicAttack",
        "rising-edge": "SkillAction",
        "iron-guard": "Guard",
        "second-wind": "CastRelease",
        "jade-tempest": "SpinAttack",
        "dodge": "Dash",
        "potion": "ItemUse"
      },
      "actions": {
        "Walk": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Run": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Sprint": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Hit": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Death": {
          "frames": 20,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Interact": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Pickup": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "ItemUse": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Sit": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Respawn": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Idle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "CombatIdle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "BasicAttack": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "SkillAction": {
          "frames": 32,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "CastChannel": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": true
        },
        "CastRelease": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "Guard": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Dash": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "SpinAttack": {
          "frames": 32,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        }
      }
    },
    "12": {
      "id": "mage",
      "name": "Mage",
      "archetype": "mage",
      "clips": [
        "Walk",
        "Run",
        "Sprint",
        "Hit",
        "Death",
        "Interact",
        "Pickup",
        "ItemUse",
        "Sit",
        "Respawn",
        "Idle",
        "CombatIdle",
        "BasicAttack",
        "SkillAction",
        "CastChannel",
        "CastRelease",
        "Guard",
        "Blink"
      ],
      "combatBindings": {
        "attack": "BasicAttack",
        "arcane-bolt": "BasicAttack",
        "ember-bloom": "CastRelease",
        "frost-ward": "Guard",
        "aether-mend": "CastRelease",
        "tempest": "CastRelease",
        "dodge": "Blink",
        "potion": "ItemUse"
      },
      "actions": {
        "Walk": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Run": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Sprint": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Hit": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Death": {
          "frames": 20,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Interact": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Pickup": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "ItemUse": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Sit": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Respawn": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Idle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "CombatIdle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "BasicAttack": {
          "frames": 24,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "SkillAction": {
          "frames": 24,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "CastChannel": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": true
        },
        "CastRelease": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "Guard": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Blink": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        }
      }
    },
    "3": {
      "id": "archer",
      "name": "Archer",
      "archetype": "ranger",
      "clips": [
        "Walk",
        "Run",
        "Sprint",
        "Hit",
        "Death",
        "Interact",
        "Pickup",
        "ItemUse",
        "Sit",
        "Respawn",
        "Idle",
        "CombatIdle",
        "BasicAttack",
        "SkillAction",
        "CastChannel",
        "CastRelease",
        "Guard",
        "Dash",
        "TrapPlace",
        "ArrowRain"
      ],
      "combatBindings": {
        "attack": "BasicAttack",
        "arrow": "BasicAttack",
        "piercing-arrow": "SkillAction",
        "thorn-snare": "TrapPlace",
        "field-aid": "ItemUse",
        "arrow-rain": "ArrowRain",
        "dodge": "Dash",
        "potion": "ItemUse"
      },
      "actions": {
        "Walk": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Run": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Sprint": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Hit": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Death": {
          "frames": 20,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Interact": {
          "frames": 12,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Pickup": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "ItemUse": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Sit": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Respawn": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "Idle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "CombatIdle": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "BasicAttack": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "SkillAction": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "CastChannel": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": true
        },
        "CastRelease": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        },
        "Guard": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": true
        },
        "Dash": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "TrapPlace": {
          "frames": 16,
          "directions": [
            "S",
            "SW",
            "W",
            "NW",
            "N",
            "NE",
            "E",
            "SE"
          ],
          "directionMap": {
            "S": "S",
            "SW": "SW",
            "W": "W",
            "NW": "NW",
            "N": "N",
            "NE": "NE",
            "E": "E",
            "SE": "SE"
          },
          "loop": false
        },
        "ArrowRain": {
          "frames": 16,
          "directions": [
            "SW",
            "NW",
            "NE",
            "SE"
          ],
          "directionMap": {
            "S": "SE",
            "SW": "SW",
            "W": "SW",
            "NW": "NW",
            "N": "NW",
            "NE": "NE",
            "E": "NE",
            "SE": "SE"
          },
          "loop": false
        }
      }
    }
  },
  "characters": {
    "swordsman/male": {
      "id": "swordsman-male-patch001",
      "definition": "./assets/characters/swordsman-male-patch001/sprite.json",
      "fitId": "astraeon-male-v3"
    },
    "swordsman/female": {
      "id": "swordsman-female-patch001",
      "definition": "./assets/characters/swordsman-female-patch001/sprite.json",
      "fitId": "astraeon-female-v3"
    },
    "mage/male": {
      "id": "mage-male-patch001",
      "definition": "./assets/characters/mage-male-patch001/sprite.json",
      "fitId": "astraeon-male-v3"
    },
    "mage/female": {
      "id": "mage-female-patch001",
      "definition": "./assets/characters/mage-female-patch001/sprite.json",
      "fitId": "astraeon-female-v3"
    },
    "archer/male": {
      "id": "archer-male-patch001",
      "definition": "./assets/characters/archer-male-patch001/sprite.json",
      "fitId": "astraeon-male-v3"
    },
    "archer/female": {
      "id": "archer-female-patch001",
      "definition": "./assets/characters/archer-female-patch001/sprite.json",
      "fitId": "astraeon-female-v3"
    }
  },
  "mirroring": "none",
  "artReady": false
});
function classFor(index){return policy.classes[index]||null}
function characterFor(index,body){const c=classFor(index);return c?policy.characters[c.id+'/'+body]||null:null}
function clipsFor(index){return classFor(index)?.clips||[]}
function actionClip(index,id){return classFor(index)?.combatBindings[id]||null}
function validatePackage(d,index,body){
 const errors=[],c=classFor(index),character=characterFor(index,body);
 if(!character)return ['Unsupported patch class/body'];
 if(d.characterId!==character.id||d.classId!==c.name||d.bodyVariant!==body)errors.push('Character identity differs from selected class/body');
 for(const [key,value]of Object.entries(policy.anatomy))if(d.canvas?.[key]!==value)errors.push('Patch anatomy differs: '+key);
 if(d.mirroring!=='none'||d.layerMode!=='visible-cutout')errors.push('Patch needs real views and visible cutouts');
 for(const [name,expected]of Object.entries(c.actions)){
  const clip=d.clips?.[name];if(!clip){errors.push('Missing animation '+name);continue}
  if(clip.tags?.includes('PENDING_PRODUCTION'))errors.push('Pending animation '+name);
  if(clip.durations?.length!==expected.frames||clip.loop!==expected.loop)errors.push('Animation timeline differs: '+name);
  const authored=clip.authoredDirections||Object.keys(clip.directions||{});
  if(JSON.stringify(authored)!==JSON.stringify(expected.directions))errors.push('Authored direction policy differs: '+name);
  if(expected.directions.length===4&&JSON.stringify(clip.directionMap)!==JSON.stringify(expected.directionMap))errors.push('Facing map differs: '+name);
 }
 return errors;
}
const api=Object.freeze({policy,classFor,characterFor,clipsFor,actionClip,validatePackage});scope.AstraeonPatch001Characters=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
