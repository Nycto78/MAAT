def __init__(self, panel_principal):
    super().__init__()
    self.panel = panel_principal
    
    # Servicio base (usando tu repositorio MySQL existente)
    from infrastructure.repositories.repositorio_mysql import RepositorioMySQL
    repositorio = RepositorioMySQL()
    
    # Crear servicio decorado
    from patterns.decorator.validacion_decorator import ValidacionStockDecorator
    from patterns.decorator.auditoria_decorator import AuditoriaDecorator
    
    self.servicio_inventario = AuditoriaDecorator(
        ValidacionStockDecorator(
            repositorio
        )
    )
    