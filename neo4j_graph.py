from neo4j import GraphDatabase

class Neo4jCallGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_edge(self, caller, callee):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_return_relationship, caller, callee)

    @staticmethod
    def _create_and_return_relationship(tx, caller, callee):
        query = (
            "MERGE (c:Function {name: $caller}) "
            "MERGE (e:Function {name: $callee}) "
            "MERGE (c)-[:CALLS]->(e)"
        )
        result = tx.run(query, caller=caller, callee=callee)
        return result.single()

    def get_impacted_functions(self, changed_functions):
        with self.driver.session() as session:
            return session.read_transaction(self._get_impacted_functions, changed_functions)

    @staticmethod
    def _get_impacted_functions(tx, changed_functions):
        query = (
            "MATCH (f:Function) "
            "WHERE f.name IN $changed_functions "
            "WITH f "
            "MATCH (f)-[:CALLS*]->(impacted:Function) "
            "RETURN DISTINCT impacted.name AS impacted_function"
        )
        result = tx.run(query, changed_functions=changed_functions)
        return [record["impacted_function"] for record in result]

# Usage
uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

call_graph = Neo4jCallGraph(uri, user, password)

# Add edges
call_graph.add_edge("function_a", "function_b")
call_graph.add_edge("function_b", "function_c")

# Get impacted functions
changed_functions = ["function_a"]
impacted_functions = call_graph.get_impacted_functions(changed_functions)
print(f"Impacted functions: {impacted_functions}")

call_graph.close()