import inspect
import IndicTransToolkit.processor as p

print('MODULE', p.__file__)
print('HAS PRE', hasattr(p.IndicProcessor, 'preprocess_batch'))
print('SIG PRE', inspect.signature(p.IndicProcessor.preprocess_batch))
print(inspect.getsource(p.IndicProcessor.preprocess_batch)[:4000])
print('---POST---')
print(inspect.signature(p.IndicProcessor.postprocess_batch))
print(inspect.getsource(p.IndicProcessor.postprocess_batch)[:3000])
