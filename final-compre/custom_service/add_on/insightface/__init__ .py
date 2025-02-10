from custom_service.add_on.insightface.dependencies import get_mxnet

requirements = get_mxnet() + ('insightface==0.1.5',)
requirements = ('mxnet-cu117==1.9.1','insightface==0.1.5',)