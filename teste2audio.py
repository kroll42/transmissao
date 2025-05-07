import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Callable
from scipy.io import wavfile
import os

class DigitalEncoder:
    """
    Classe para codificar e decodificar dados usando diferentes técnicas
    de codificação digital.
    """
    
    def __init__(self):
        # Dicionário de codificações disponíveis
        self.encoding_methods = {
            "Manchester": self.manchester_encode,
            "NRZ": self.nrz_encode,
            "NRZI": self.nrzi_encode,
            "AMI": self.ami_encode,
            "Biphase_Mark": self.biphase_mark_encode,
            "Biphase_Space": self.biphase_space_encode,
            "Differential_Manchester": self.differential_manchester_encode,
        }
        
        # Dicionário de métodos de decodificação
        self.decoding_methods = {
            "Manchester": self.manchester_decode,
            "NRZ": self.nrz_decode,
            "NRZI": self.nrzi_decode,
            "AMI": self.ami_decode,
            "Biphase_Mark": self.biphase_mark_decode,
            "Biphase_Space": self.biphase_space_decode,
            "Differential_Manchester": self.differential_manchester_decode,
        }
    
    def get_available_encodings(self) -> List[str]:
        """Retorna uma lista de codificações disponíveis."""
        return list(self.encoding_methods.keys())
    
    # ========== Métodos de codificação ==========
    
    def manchester_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação Manchester:
        - 0 é representado por transição baixo-alto (01)
        - 1 é representado por transição alto-baixo (10)
        """
        encoded = []
        for bit in binary_data:
            if bit == 0:
                encoded.extend([0, 1])  # Transição baixo-alto para 0
            else:
                encoded.extend([1, 0])  # Transição alto-baixo para 1
        return encoded
    
    def nrz_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação NRZ (Non-Return to Zero):
        - 0 é representado por nível baixo
        - 1 é representado por nível alto
        """
        encoded = []
        for bit in binary_data:
            encoded.append(bit)
        return encoded
    
    def nrzi_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação NRZI (Non-Return to Zero Inverted):
        - 0 mantém o nível atual
        - 1 inverte o nível atual
        """
        encoded = []
        level = 0  # Nível inicial
        
        for bit in binary_data:
            if bit == 0:
                encoded.append(level)  # Mantém o nível
            else:
                level = 1 - level  # Inverte o nível (0->1 ou 1->0)
                encoded.append(level)
        
        return encoded
    
    def ami_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação AMI (Alternate Mark Inversion):
        - 0 é representado por nível zero
        - 1 alterna entre níveis positivo (+1) e negativo (-1)
        """
        encoded = []
        last_polarity = 1  # Começa com positivo
        
        for bit in binary_data:
            if bit == 0:
                encoded.append(0)  # Zero sempre é nível zero
            else:
                last_polarity = -last_polarity  # Alterna entre +1 e -1
                encoded.append(last_polarity)
        
        return encoded
    
    def biphase_mark_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação Biphase Mark:
        - Sempre há uma transição no meio do intervalo do bit
        - Bit 1 tem uma transição adicional no início do intervalo
        - Bit 0 não tem transição adicional
        """
        encoded = []
        level = 0
        
        for bit in binary_data:
            if bit == 1:
                # Transição no início
                level = 1 - level
            
            encoded.append(level)
            
            # Transição no meio (para ambos 0 e 1)
            level = 1 - level
            encoded.append(level)
        
        return encoded
    
    def biphase_space_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação Biphase Space:
        - Sempre há uma transição no meio do intervalo do bit
        - Bit 0 tem uma transição adicional no início do intervalo
        - Bit 1 não tem transição adicional
        """
        encoded = []
        level = 0
        
        for bit in binary_data:
            if bit == 0:
                # Transição no início
                level = 1 - level
            
            encoded.append(level)
            
            # Transição no meio (para ambos 0 e 1)
            level = 1 - level
            encoded.append(level)
        
        return encoded
    
    def differential_manchester_encode(self, binary_data: List[int]) -> List[int]:
        """
        Codificação Manchester Diferencial:
        - Sempre há uma transição no meio do intervalo do bit
        - Bit 0 causa uma transição no início do intervalo seguinte
        - Bit 1 não causa transição no início do intervalo seguinte
        """
        encoded = []
        level = 0
        
        for bit in binary_data:
            if bit == 0:
                # Para 0, mantém o mesmo padrão do bit anterior
                encoded.append(level)
                level = 1 - level  # Transição no meio
                encoded.append(level)
            else:
                # Para 1, inverte o padrão
                level = 1 - level  # Transição no início
                encoded.append(level)
                level = 1 - level  # Transição no meio
                encoded.append(level)
        
        return encoded
    
    # ========== Métodos de decodificação ==========
    
    def manchester_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em Manchester."""
        decoded = []
        i = 0
        
        # Assegurar que estamos processando pares completos
        while i < len(encoded_data) - 1:
            # Verificar transição
            if encoded_data[i] == 0 and encoded_data[i+1] == 1:
                decoded.append(0)  # Transição baixo-alto é 0
            elif encoded_data[i] == 1 and encoded_data[i+1] == 0:
                decoded.append(1)  # Transição alto-baixo é 1
            else:
                # Erro de codificação
                print(f"Aviso de erro na decodificação Manchester na posição {i}, corrigindo...")
                # Estratégia de correção: assumir o último bit válido ou 0 se for o primeiro
                if decoded:
                    decoded.append(decoded[-1])  # Repetir o último bit decodificado
                else:
                    decoded.append(0)  # Se for o primeiro bit, assume 0
            
            i += 2  # Avança dois bits (um símbolo Manchester completo)
        
        # Verificar se o comprimento está correto para dados ASCII (múltiplo de 8)
        if len(decoded) % 8 != 0:
            # Adicionar bits para completar o último byte
            padding_needed = 8 - (len(decoded) % 8)
            decoded.extend([0] * padding_needed)
            print(f"Adicionados {padding_needed} bits de padding para completar o último byte")
            
        return decoded
    
    def nrz_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em NRZ."""
        return encoded_data  # NRZ é direto, o bit é o próprio nível
    
    def nrzi_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em NRZI."""
        decoded = []
        
        for i in range(1, len(encoded_data)):
            # Se o nível mudou, temos um bit 1, senão um bit 0
            if encoded_data[i] != encoded_data[i-1]:
                decoded.append(1)
            else:
                decoded.append(0)
        
        return decoded
    
    def ami_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em AMI."""
        decoded = []
        
        for level in encoded_data:
            if level == 0:
                decoded.append(0)
            else:  # +1 ou -1
                decoded.append(1)
        
        return decoded
    
    def biphase_mark_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em Biphase Mark."""
        decoded = []
        i = 0
        
        while i < len(encoded_data) - 1:
            # Verifica se há transição no início do bit (comparando com bit anterior)
            if i > 0 and encoded_data[i-1] != encoded_data[i]:
                decoded.append(1)  # Transição no início indica bit 1
            else:
                decoded.append(0)  # Sem transição no início indica bit 0
            
            i += 2  # Pula para o próximo par de bits
        
        return decoded
    
    def biphase_space_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em Biphase Space."""
        decoded = []
        i = 0
        
        while i < len(encoded_data) - 1:
            # Verifica se há transição no início do bit (comparando com bit anterior)
            if i > 0 and encoded_data[i-1] != encoded_data[i]:
                decoded.append(0)  # Transição no início indica bit 0
            else:
                decoded.append(1)  # Sem transição no início indica bit 1
            
            i += 2  # Pula para o próximo par de bits
        
        return decoded
    
    def differential_manchester_decode(self, encoded_data: List[int]) -> List[int]:
        """Decodifica dados codificados em Manchester Diferencial."""
        decoded = []
        i = 0
        
        while i < len(encoded_data) - 3:
            # Verifica transições entre símbolos consecutivos
            current_first = encoded_data[i]
            next_first = encoded_data[i+2]
            
            if current_first == next_first:
                # Sem transição no início do próximo símbolo = bit 1
                decoded.append(1)
            else:
                # Com transição no início do próximo símbolo = bit 0
                decoded.append(0)
            
            i += 2  # Avança para o próximo símbolo
        
        return decoded
    
    # ========== Funções principais ==========
    
    def encode(self, binary_data: List[int], method: str = "Manchester") -> List[int]:
        """
        Codifica dados binários usando o método especificado.
        
        Args:
            binary_data: Lista de bits (0s e 1s) para codificar
            method: Método de codificação a ser utilizado
            
        Returns:
            Lista de valores codificados
        """
        if method not in self.encoding_methods:
            raise ValueError(f"Método de codificação '{method}' não implementado")
        
        return self.encoding_methods[method](binary_data)
    
    def decode(self, encoded_data: List[int], method: str = "Manchester") -> List[int]:
        """
        Decodifica dados codificados usando o método especificado.
        
        Args:
            encoded_data: Lista de valores codificados
            method: Método de decodificação a ser utilizado
            
        Returns:
            Lista de bits (0s e 1s) decodificados
        """
        if method not in self.decoding_methods:
            raise ValueError(f"Método de decodificação '{method}' não implementado")
        
        return self.decoding_methods[method](encoded_data)
    
    def visualize_waveform(self, data: List[int], method: str = None, title: str = None) -> None:
        """
        Visualiza os dados como forma de onda digital.
        
        Args:
            data: Lista de valores de sinal (0s, 1s ou -1s para AMI)
            method: Método de codificação (para o título)
            title: Título personalizado do gráfico
        """
        # Duplicar cada valor para criar uma forma de onda com patamares
        waveform = []
        for value in data:
            waveform.extend([value, value])
        
        # Para visualização mais clara
        time = np.arange(len(waveform))
        
        plt.figure(figsize=(12, 4))
        plt.step(time, waveform, where='post', linewidth=2)
        
        # Limites e linhas de grade
        plt.ylim([-1.5, 1.5])
        plt.grid(True)
        
        # Título e rótulos
        if title:
            plt.title(title)
        elif method:
            plt.title(f"Codificação {method}")
        else:
            plt.title("Forma de Onda Digital")
            
        plt.xlabel("Tempo")
        plt.ylabel("Amplitude")
        
        # Mostrar marcadores de bit
        bit_positions = np.arange(0, len(waveform), 2)
        plt.xticks(bit_positions, [f"{i//2}" for i in bit_positions])
        
        plt.tight_layout()
        plt.show()
    
    def save_audio_waveform(self, data: List[int], filename: str = "digital_signal.wav", 
                           sample_rate: int = 44100, bit_rate: int = 300) -> str:
        """
        Converte sinal digital codificado em arquivo de áudio WAV.
        
        Args:
            data: Lista de valores de sinal codificado (0s, 1s ou -1s para AMI)
            filename: Nome do arquivo de saída
            sample_rate: Taxa de amostragem em Hz
            bit_rate: Taxa de bits por segundo
            
        Returns:
            Caminho para o arquivo de áudio salvo
        """
        # Determinar amostras por bit
        samples_per_bit = int(sample_rate / bit_rate)
        
        # Expandir cada bit do sinal para várias amostras
        audio_signal = []
        for value in data:
            # Converter o valor digital (-1, 0, 1) para uma amplitude de áudio (-0.5, 0, 0.5)
            # Multiplica por 0.5 para evitar clipping
            amplitude = float(value) * 0.5
            
            # Repetir o valor para criar um pulso com duração adequada
            audio_signal.extend([amplitude] * samples_per_bit)
        
        # Converter para array numpy
        audio_array = np.array(audio_signal, dtype=np.float32)
        
        # Normalizar entre -1 e 1 para evitar clipping
        if np.max(np.abs(audio_array)) > 0:
            audio_array = audio_array / np.max(np.abs(audio_array)) * 0.9
        
        # Salvar como arquivo WAV
        wavfile.write(filename, sample_rate, audio_array)
        
        # Retornar o caminho absoluto do arquivo salvo
        return os.path.abspath(filename)


class TransmissionSystem:
    """
    Sistema completo de transmissão digital, incluindo codificação,
    simulação de canal e decodificação.
    """
    
    def __init__(self):
        self.encoder = DigitalEncoder()
        
    def string_to_binary(self, text: str) -> List[int]:
        """Converte uma string para uma lista de bits."""
        binary = []
        for char in text:
            # Converter cada caractere para seu valor ASCII e depois para binário
            ascii_val = ord(char)
            for i in range(7, -1, -1):  # 8 bits para cada caractere
                binary.append((ascii_val >> i) & 1)
        return binary
    
    def binary_to_string(self, binary: List[int]) -> str:
        """Converte uma lista de bits para string."""
        result = ""
        for i in range(0, len(binary), 8):
            # Garantir que temos um byte completo
            if i + 8 <= len(binary):
                byte = binary[i:i+8]
                char_code = sum(bit << (7-j) for j, bit in enumerate(byte))
                result += chr(char_code)
        return result
    
    def binary_to_hex(self, binary: List[int]) -> str:
        """Converte uma lista de bits para representação hexadecimal."""
        hex_result = ""
        for i in range(0, len(binary), 4):
            if i + 4 <= len(binary):
                nibble = binary[i:i+4]
                hex_value = sum(bit << (3-j) for j, bit in enumerate(nibble))
                hex_result += format(hex_value, 'x').upper()
        return hex_result
    
    def simulate_channel(self, encoded_data: List[int], noise_level: float = 0.0) -> List[int]:
        """
        Simula um canal de transmissão com possível adição de ruído.
        
        Args:
            encoded_data: Lista de valores codificados
            noise_level: Probabilidade de um bit ser invertido (0 a 1)
            
        Returns:
            Lista de valores possivelmente modificados pelo ruído
        """
        if noise_level <= 0:
            return encoded_data.copy()
        
        noisy_data = []
        for bit in encoded_data:
            # Adicionar ruído (inversão de bit) com probabilidade noise_level
            if np.random.random() < noise_level:
                if bit == 0:
                    noisy_data.append(1)
                elif bit == 1:
                    noisy_data.append(0)
                else:  # Para AMI (-1)
                    noisy_data.append(0)  # Simplificação para AMI
            else:
                noisy_data.append(bit)
        
        return noisy_data
    
    def transmit(self, input_data: str, encoding_method: str = "Manchester", 
                 noise_level: float = 0.0, visualize: bool = True) -> Tuple[str, List[int], List[int]]:
        """
        Realiza todo o processo de transmissão: codificação, simulação de canal e decodificação.
        
        Args:
            input_data: String de entrada para transmitir
            encoding_method: Método de codificação a ser utilizado
            noise_level: Nível de ruído no canal (0 a 1)
            visualize: Se True, exibe visualizações das formas de onda
            
        Returns:
            Tupla com (dados decodificados como string, dados originais como bits, dados decodificados como bits)
        """
        # Converter entrada para binário
        binary_data = self.string_to_binary(input_data)
        
        # Codificar
        encoded_data = self.encoder.encode(binary_data, encoding_method)
        
        # Simular canal com ruído
        transmitted_data = self.simulate_channel(encoded_data, noise_level)
        
        # Decodificar
        decoded_data = self.encoder.decode(transmitted_data, encoding_method)
        
        # Converter binário de volta para string
        output_data = self.binary_to_string(decoded_data)
        
        # Visualizar conforme selecionado pelo usuário
        if visualize:
            self.visualize_menu(binary_data, encoded_data, transmitted_data, decoded_data, encoding_method, noise_level)
        
        return output_data, binary_data, decoded_data
    
    def save_audio(self, encoded_data: List[int], method: str, filename: str = None, 
                  bit_rate: int = 300) -> str:
        """
        Salva os dados codificados como arquivo de áudio.
        
        Args:
            encoded_data: Dados codificados a serem salvos
            method: Método de codificação utilizado
            filename: Nome do arquivo (opcional)
            bit_rate: Taxa de bits por segundo
            
        Returns:
            Caminho do arquivo salvo
        """
        # Criar nome de arquivo se não fornecido
        if filename is None:
            filename = f"encoded_{method}_{len(encoded_data)}_bits.wav"
        
        # Salvar como áudio
        audio_path = self.encoder.save_audio_waveform(encoded_data, filename, bit_rate=bit_rate)
        
        return audio_path
    
    def visualize_menu(self, binary_data, encoded_data, transmitted_data, decoded_data, encoding_method, noise_level):
        """
        Exibe um menu para selecionar quais gráficos visualizar.
        """
        while True:
            print("\n===== MENU DE VISUALIZAÇÃO =====")
            print("1. Visualizar dados binários originais")
            print("2. Visualizar dados codificados")
            print("3. Visualizar dados transmitidos (com ruído)")
            print("4. Visualizar dados decodificados")
            print("5. Visualizar todos os gráficos")
            print("6. Salvar como áudio")
            print("7. Voltar ao menu principal")
            
            try:
                choice = int(input("\nEscolha uma opção (1-7): "))
                
                if choice == 1:
                    print("\nOs dados representados são digitais (sequências de 0s e 1s).")
                    self.encoder.visualize_waveform(binary_data, None, "Dados Binários Originais")
                elif choice == 2:
                    print("\nOs dados representados são digitais (codificados).")
                    self.encoder.visualize_waveform(encoded_data, encoding_method, f"Dados Codificados ({encoding_method})")
                elif choice == 3:
                    print("\nOs dados representados são digitais (com possível ruído).")
                    self.encoder.visualize_waveform(transmitted_data, None, f"Dados Transmitidos (Ruído: {noise_level})")
                elif choice == 4:
                    print("\nOs dados representados são digitais (recuperados após decodificação).")
                    self.encoder.visualize_waveform(decoded_data, None, "Dados Decodificados")
                elif choice == 5:
                    print("\nTodos os dados representados são digitais em diferentes estágios do processo.")
                    self.encoder.visualize_waveform(binary_data, None, "Dados Binários Originais")
                    self.encoder.visualize_waveform(encoded_data, encoding_method, f"Dados Codificados ({encoding_method})")
                    if noise_level > 0:
                        self.encoder.visualize_waveform(transmitted_data, None, f"Dados Transmitidos (Ruído: {noise_level})")
                    self.encoder.visualize_waveform(decoded_data, None, "Dados Decodificados")
                elif choice == 6:
                    # Submenu para salvar áudio
                    print("\n--- Salvar como Áudio ---")
                    print("1. Salvar dados originais")
                    print("2. Salvar dados codificados")
                    print("3. Salvar dados transmitidos (com ruído)")
                    print("4. Salvar dados decodificados")
                    
                    audio_choice = int(input("\nEscolha qual sinal salvar (1-4): "))
                    
                    # Obter taxa de bits
                    bit_rate_str = input("Taxa de bits (Hz, padrão 300): ")
                    bit_rate = int(bit_rate_str) if bit_rate_str else 300
                    
                    # Obter nome do arquivo
                    custom_filename = input("Nome do arquivo (deixe em branco para nome automático): ")
                    
                    # Salvar o áudio apropriado
                    if audio_choice == 1:
                        filename = custom_filename or f"binary_original.wav"
                        path = self.save_audio(binary_data, "Binary", filename, bit_rate)
                    elif audio_choice == 2:
                        filename = custom_filename or f"encoded_{encoding_method}.wav"
                        path = self.save_audio(encoded_data, encoding_method, filename, bit_rate)
                    elif audio_choice == 3:
                        filename = custom_filename or f"transmitted_{encoding_method}_noise_{noise_level}.wav"
                        path = self.save_audio(transmitted_data, f"{encoding_method}_noise", filename, bit_rate)
                    elif audio_choice == 4:
                        filename = custom_filename or f"decoded_{encoding_method}.wav"
                        path = self.save_audio(decoded_data, "Decoded", filename, bit_rate)
                    else:
                        print("Opção inválida.")
                        continue
                    
                    print(f"\nÁudio salvo em: {path}")
                    
                elif choice == 7:
                    break
                else:
                    print("Opção inválida, tente novamente.")
            except ValueError:
                print("Entrada inválida. Digite um número entre 1 e 7.")


# Menu principal com interface de texto
def main_menu():
    ts = TransmissionSystem()
    
    while True:
        print("\n============ SISTEMA DE CODIFICAÇÃO DIGITAL ============")
        print("1. Transmitir dados")
        print("2. Visualizar métodos de codificação disponíveis")
        print("3. Analisar exemplos específicos (BA 0000, NA 0010)")
        print("4. Sobre dados digitais")
        print("5. Converter sinal para áudio")
        print("6. Sair")
        
        try:
            choice = int(input("\nEscolha uma opção (1-6): "))
            
            if choice == 1:
                # Submenu de transmissão
                input_text = input("\nDigite o texto a ser transmitido: ")
                
                # Escolher método de codificação
                methods = ts.encoder.get_available_encodings()
                print("\nMétodos de codificação disponíveis:")
                for i, method in enumerate(methods, 1):
                    print(f"{i}. {method}")
                
                method_idx = int(input("\nEscolha um método de codificação (número): ")) - 1
                if 0 <= method_idx < len(methods):
                    encoding_method = methods[method_idx]
                else:
                    print("Opção inválida, usando Manchester como padrão.")
                    encoding_method = "Manchester"
                
                # Configurar nível de ruído
                noise_str = input("\nNível de ruído (0.0 a 1.0, padrão 0.0): ")
                try:
                    noise_level = float(noise_str) if noise_str else 0.0
                    if not (0 <= noise_level <= 1):
                        print("Valor fora do intervalo permitido, usando 0.0.")
                        noise_level = 0.0
                except ValueError:
                    print("Valor inválido, usando 0.0.")
                    noise_level = 0.0
                
                # Realizar transmissão
                output_text, original_bits, decoded_bits = ts.transmit(
                    input_text, 
                    encoding_method=encoding_method,
                    noise_level=noise_level,
                    visualize=True  # Agora o menu de visualização será exibido
                )
                
                print(f"\nTexto original: {input_text}")
                print(f"Bits originais: {original_bits[:24]}..." if len(original_bits) > 24 else f"Bits originais: {original_bits}")
                print(f"Bits decodificados: {decoded_bits[:24]}..." if len(decoded_bits) > 24 else f"Bits decodificados: {decoded_bits}")
                print(f"Texto recebido: {output_text}")
                
                # Perguntar se deseja salvar como áudio
                save_audio = input("\nDeseja salvar o sinal codificado como áudio? (s/n): ")
                if save_audio.lower() == 's':
                    # Obter taxa de bits
                    bit_rate_str = input("Taxa de bits (Hz, padrão 300): ")
                    bit_rate = int(bit_rate_str) if bit_rate_str else 300
                    
                    # Obter nome do arquivo
                    filename = input("Nome do arquivo (deixe em branco para nome automático): ")
                    if not filename:
                        filename = f"encoded_{encoding_method}_{input_text[:10]}.wav"
                    
                    # Salvar como áudio
                    audio_path = ts.save_audio(ts.encoder.encode(original_bits, encoding_method), 
                                              encoding_method, filename, bit_rate)
                    print(f"\nÁudio salvo em: {audio_path}")
                
            elif choice == 2:
                methods = ts.encoder.get_available_encodings()
                print("\nMétodos de codificação disponíveis:")
                for i, method in enumerate(methods, 1):
                    print(f"{i}. {method}")
                
                input("\nPressione Enter para continuar...")
                
            elif choice == 3:
                # Análise de exemplos específicos
                print("\n=== Análise de Exemplos Específicos ===")
                print("BA (Bi-Alternate): 0000")
                print("NA (Non-Alternate): 0010")
                
                # Exemplos de codificação
                bits_example = "0000"
                
                print("\nBA (Bi-Alternate Mark Inversion) para bits '0000':")
                ba_encoded = ts.encoder.bami_encode(bits_example)
                print("Codificado: ", end="")
                for bit in ba_encoded:
                    print("▀" if bit == 1 else "_", end="")
                
                print("\n\nNA (Non-Alternate Mark Inversion) para bits '0010':")
                na_encoded = ts.encoder.nami_encode("0010")
                print("Codificado: ", end="")
                for bit in na_encoded:
                    print("▀" if bit == 1 else "_", end="")
                
                input("\nPressione Enter para continuar...")
                
            elif choice == 4:
                # Sobre dados digitais
                print("\n=== Sobre Dados Digitais ===")
                print("Dados digitais são representações discretas de informação usando sistemas binários.")
                print("Eles são a base para todas as formas modernas de comunicação eletrônica e armazenamento.")
                print("\nCodificação de Linha é a forma como os bits são representados em um sinal físico.")
                print("Diferentes métodos de codificação oferecem vantagens em termos de:")
                print("- Sincronização de clock")
                print("- Detecção de erros")
                print("- Eficiência de largura de banda")
                print("- Imunidade ao ruído")
                
                input("\nPressione Enter para continuar...")
                
            elif choice == 5:
                # Converter sinal para áudio
                print("\n=== Converter Sinal para Áudio ===")
                
                # Input do usuário para texto
                input_text = input("Digite o texto para converter em áudio: ")
                
                # Escolher método de codificação
                methods = ts.encoder.get_available_encodings()
                print("\nMétodos de codificação disponíveis:")
                for i, method in enumerate(methods, 1):
                    print(f"{i}. {method}")
                
                method_idx = int(input("\nEscolha um método de codificação (número): ")) - 1
                if 0 <= method_idx < len(methods):
                    encoding_method = methods[method_idx]
                else:
                    print("Opção inválida, usando Manchester como padrão.")
                    encoding_method = "Manchester"
                
                # Obter taxa de bits
                bit_rate_str = input("Taxa de bits (Hz, padrão 300): ")
                bit_rate = int(bit_rate_str) if bit_rate_str else 300
                
                # Obter nome do arquivo
                filename = input("Nome do arquivo (deixe em branco para nome automático): ")
                if not filename:
                    filename = f"encoded_{encoding_method}_{input_text[:10]}.wav"
                
                # Converter texto para bits
                bits = ts.text_to_bits(input_text)
                
                # Salvar como áudio
                audio_path = ts.save_audio(ts.encoder.encode(bits, encoding_method), 
                                          encoding_method, filename, bit_rate)
                print(f"\nÁudio salvo em: {audio_path}")
                
                input("\nPressione Enter para continuar...")
                
            elif choice == 6:
                print("\nSaindo do sistema...")
                break
                
            else:
                print("\nOpção inválida. Por favor, escolha entre 1 e 6.")
                
        except ValueError:
            print("\nEntrada inválida. Por favor, insira um número válido.")
        except Exception as e:
            print(f"\nOcorreu um erro: {e}")


# Executa o menu principal quando o script é executado diretamente
if __name__ == "__main__":
    main_menu()