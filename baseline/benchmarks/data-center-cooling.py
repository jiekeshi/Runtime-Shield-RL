import sys
sys.path.append(".")

from main import *
from shield import Shield
from Environment import Environment
from DDPG import *
import argparse

def cooling (learning_method, number_of_rollouts, simulation_steps, learning_eposides, critic_structure, actor_structure, train_dir,\
            nn_test=False, retrain_shield=False, shield_test=False, test_episodes=100, retrain_nn=False):
  A = np.matrix([
    [1.01,0.01,0],
    [0.01,1.01,0.01],
    [0.0,0.01,1.01]])
  B = np.matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]])

  #intial state space
  s_min = np.array([[  1.6],[ 1.6], [1.6]])
  s_max = np.array([[  3.2],[ 3.2], [3.2]])

  Q = np.eye(3)
  R = np.eye(3)

  x_min = np.array([[-3.2],[-3.2],[-3.2]])
  x_max = np.array([[3.2],[3.2],[3.2]])
  u_min = np.array([[-1.],[-1.],[-1.]])
  u_max = np.array([[ 1.],[ 1.],[ 1.]])

  env = Environment(A, B, u_min, u_max, s_min, s_max, x_min, x_max, Q, R, bad_reward=-1000)

  if retrain_nn:
    args = { 'actor_lr': 0.001,
             'critic_lr': 0.01,
             'actor_structure': actor_structure,
             'critic_structure': critic_structure, 
             'buffer_size': 1000000,
             'gamma': 0.99,
             'max_episode_len': 100,
             'max_episodes': 1000,
             'minibatch_size': 64,
             'random_seed': 6553,
             'tau': 0.005,
             'model_path': train_dir+"retrained_model.chkp",
             'enable_test': nn_test, 
             'test_episodes': test_episodes,
             'test_episodes_len': 5000}
  else:
    args = { 'actor_lr': 0.001,
             'critic_lr': 0.01,
             'actor_structure': actor_structure,
             'critic_structure': critic_structure, 
             'buffer_size': 1000000,
             'gamma': 0.99,
             'max_episode_len': 100,
             'max_episodes': learning_eposides,
             'minibatch_size': 64,
             'random_seed': 6553,
             'tau': 0.005,
             'model_path': train_dir+"model.chkp",
             'enable_test': nn_test, 
             'test_episodes': test_episodes,
             'test_episodes_len': 5000}
  actor = DDPG(env, args)

  #################### Shield #################
  model_path = os.path.split(args['model_path'])[0]+'/'
  linear_func_model_name = 'K.model'
  model_path = model_path+linear_func_model_name+'.npy'

  names = {0:"cart position, meters", 1:"cart velocity", 2:"pendulum angle, radians", 3:"pendulum angle velocity"}
  shield = Shield(env, actor, model_path, force_learning=retrain_shield)
  shield.train_shield(learning_method, number_of_rollouts, simulation_steps, names=names, explore_mag = 0.02, step_size = 0.0025)
  if shield_test:
    shield.test_shield(test_episodes, 5000, mode="single")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Running Options')
  parser.add_argument('--nn_test', action="store_true", dest="nn_test")
  parser.add_argument('--retrain_shield', action="store_true", dest="retrain_shield")
  parser.add_argument('--shield_test', action="store_true", dest="shield_test")
  parser.add_argument('--test_episodes', action="store", dest="test_episodes", type=int)
  parser.add_argument('--retrain_nn', action="store_true", dest="retrain_nn")
  parser_res = parser.parse_args()
  nn_test = parser_res.nn_test
  retrain_shield = parser_res.retrain_shield
  shield_test = parser_res.shield_test
  test_episodes = parser_res.test_episodes if parser_res.test_episodes is not None else 100
  retrain_nn = parser_res.retrain_nn

  cooling("random_search", 100, 100, 0, [240, 200], [280, 240, 200], "ddpg_chkp/cooling/240200280240200/", \
    nn_test=nn_test, retrain_shield=retrain_shield, shield_test=shield_test, test_episodes=test_episodes, retrain_nn=retrain_nn)