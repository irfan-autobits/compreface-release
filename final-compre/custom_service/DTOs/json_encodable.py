class JSONEncodable:
    def to_json(self):
        if hasattr(self, 'dto'):
            return self.dto.to_json()
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
