# Laumas TLB4 Modbus Register Map
**Device:** Laumas TLB4 4-Channel Weight Transmitter
**Protocols:** Modbus RTU (RS485) / Modbus TCP
**Data Type:** 16-bit Holding Registers (Function Code 03 / 06 / 16)

---

## 1. Communication Settings (Default)
| Parameter | Value |
| :--- | :--- |
| **Baud Rate** | 9600 (2400 - 115200) |
| **Data Bits** | 8 |
| **Parity** | None |
| **Stop Bits** | 1 |
| **Modbus ID** | 1 |
| **TCP Port** | 502 |

---

## 2. Real-Time Data Registers (Read-Only)
Weights are stored as 32-bit signed integers across two registers (High Word/Low Word).

| Register (PLC) | Address (Hex) | Description | Unit/Format |
| :--- | :--- | :--- | :--- |
| **40001 - 40002** | 0000 - 0001 | **Gross Weight** | 32-bit Signed Int |
| **40003 - 40004** | 0002 - 0003 | **Net Weight** | 32-bit Signed Int |
| **40005** | 0004 | **Status Register** | Bitmask (See Section 3) |
| **40006 - 40007** | 0005 - 0006 | **Tare Weight** | 32-bit Signed Int |
| **40019 - 40020** | 0012 - 0013 | **Setpoint 1 Value** | 32-bit Signed Int |
| **40021 - 40022** | 0014 - 0015 | **Setpoint 2 Value** | 32-bit Signed Int |
| **40023 - 40024** | 0016 - 0017 | **Setpoint 3 Value** | 32-bit Signed Int |

---

## 3. Status Register (40005) Bits
| Bit | Description |
| :--- | :--- |
| **Bit 0** | **Stability:** 1 = Weight stable, 0 = Weight moving |
| **Bit 1** | **Net Mode:** 1 = Net weight, 0 = Gross weight |
| **Bit 2** | **Center of Zero:** 1 = Weight is zero |
| **Bit 3** | **Overload:** 1 = Weight exceeds capacity |
| **Bit 4** | **Underload:** 1 = Weight below minimum |
| **Bit 5** | **Error:** 1 = Cell failure / Disconnected |
| **Bit 8** | **Digital Input 1 Status** |
| **Bit 9** | **Digital Input 2 Status** |

---

## 4. Command Register (40008)
Write the following integer codes to register **40008** to trigger actions:

| Code | Action |
| :--- | :--- |
| **0001** | **Semi-Automatic Zero** (Reset Gross to 0) |
| **0002** | **Semi-Automatic Tare** (Set current weight as Tare) |
| **0003** | **Clear Tare** (Reset Tare to 0) |
| **0004** | **Switch Gross/Net** |
| **0007** | **Reset Peak** |

---

## 5. Individual Channel Readings (Raw Counts)
Monitor the health of each load cell individually. These are 24-bit counts mapped to 32-bit registers.

| Channel | Registers (PLC) | Address (Hex) | Description |
| :--- | :--- | :--- | :--- |
| **Channel 1** | 40081 - 40082 | 0050 - 0051 | Internal Divisions Ch 1 |
| **Channel 2** | 40083 - 40084 | 0052 - 0053 | Internal Divisions Ch 2 |
| **Channel 3** | 40085 - 40086 | 0054 - 0055 | Internal Divisions Ch 3 |
| **Channel 4** | 40087 - 40088 | 0056 - 0057 | Internal Divisions Ch 4 |

---

## 6. Individual Channel Configuration (Theoretical Calibration)
To set sensitivity, write to these registers. **Note:** Use 5 decimal places for sensitivity (e.g., 2.0000 mV/V = 20000).

| Channel | Capacity Reg | Sensitivity Reg | Notes |
| :--- | :--- | :--- | :--- |
| **Channel 1** | 40110 | **40111** | Ch 1 Capacity & mV/V |
| **Channel 2** | 40120 | **40121** | Ch 2 Capacity & mV/V |
| **Channel 3** | 40130 | **40131** | Ch 3 Capacity & mV/V |
| **Channel 4** | 40140 | **40141** | Ch 4 Capacity & mV/V |

---

## 7. Global Programming Parameters
| Register (PLC) | Description | Range / Values |
| :--- | :--- | :--- |
| **40101** | **Full Scale** | Max Capacity of the entire scale |
| **40102** | **Division** | Resolution (1, 2, 5, 10, 20, 50, 100) |
| **40103** | **Decimal Places** | 0 to 4 |
| **40104** | **Digital Filter** | 0 (None) to 10 (Strong) |
| **40105** | **Zero Tracking** | 0 (Off) to 5 (Max) |

---

## Developer Notes
1. **Addressing Offset:** If your PLC/Library is 0-indexed, subtract 1 from the "PLC Register" (e.g., 40001 becomes address 0).
2. **Endianness:** TLB4 uses **Big-Endian** (ABCD) by default. Some libraries may require word-swapping.
3. **EEPROM Protection:** Do not write to registers 40100+ continuously. Only write when a configuration change is required by the user.
