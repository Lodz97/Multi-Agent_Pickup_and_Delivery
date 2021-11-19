# Multi-Agent Pickup and Delivery
This repo contains implementations of various algorithms used to solve the problem of Multi-Agent Pickup and Delivery (a generalization of Multi-Agent Path Finding) and a simulation envirionment used to test them.

## Overview
Multi-Agent Pickup and Delivery (MAPD) is the problem of computing collision-free paths for a group of agents such that they can safely reach delivery locations from pickup ones.  These locations are provided at runtime, making MAPD a combination between classical Multi-Agent Path Finding (MAPF) and online task assignment. Current algorithms for MAPD do not consider many of the practical issues encountered in real applications: real agents often do not follow the planned paths perfectly, and may be subject to delays and failures.  The objectives of this work are to study the problem of MAPD with delays, and to present solution approaches that provide robustness guarantees by planning paths that limit the effects of imperfect execution. In particular, two  algorithms are introduced, k-TP and p-TP, both based on a decentralized algorithm typically used to solve MAPD, Token Passing  (TP), which offer deterministic and probabilistic guarantees,respectively. Experimentally, these algorithms are compared against a version of TP enriched with recovery routines. k-TP and p-TP, planning robustsolutions, are able to significantly reduce the number of replans caused by delays, with little or no increase in solution cost and running time.

## Simulation
In the image we can see an overview of the simulation pipeline. 
<p align="center">
    <img src="https://imgur.com/a/u6ndue5" width="350" alt="Politecnico di Milano"/>
</p>
